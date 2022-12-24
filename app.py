# -*- coding: utf-8 -*-
from typing import List

from dash import Dash, Input, Output, State, dash_table, dcc, html
from lazy import lazy

from categorizer.classifier import ZeroShotClassifier
from categorizer.main import Categorizer
from categorizer.storage import Storage
from data import load_categories

_NO_BREAKDOWN = 'None'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)


class Server:
    def __init__(self, app, storage, categorizer):
        self.app = app
        self.storage = storage
        self.categorizer = categorizer
        self.creat_app()

    @lazy
    def categories(self):
        return load_categories()

    def creat_app(self):
        parent_categories = self.categories.parent_category.unique()

        categories_div = []
        for parent_category in parent_categories:
            category_div = []
            parent_category_name = parent_category.lower().replace(' ', '-')
            category_div.append(
                dcc.Checklist([parent_category], id=parent_category_name)
            )
            breakdown = [_NO_BREAKDOWN] + list(
                self.categories[
                    self.categories.parent_category == parent_category
                ].breakdown_by.unique()
            )
            category_div.append(
                dcc.RadioItems(
                    breakdown,
                    _NO_BREAKDOWN,
                    id=f'{parent_category_name}-breakdown-by',
                    style={'display': 'none'},
                )
            )
            category_div.append(
                dcc.Checklist(
                    [], id=f'{parent_category_name}-children', style={'display': 'none'}
                )
            )
            categories_div.append(
                html.Div(category_div, style={'padding': 5, 'width': '20%'})
            )

        slider = html.Div(
            [
                'You may select threshold:',
                dcc.Slider(
                    0,
                    1,
                    value=0,
                    marks={0: '0', 1: '1'},
                    tooltip={'placement': 'bottom', 'always_visible': True},
                    id='threshold',
                ),
            ],
            style={'width': '30%', 'margin-top': 10},
        )

        documents_dropdown = dcc.Dropdown(
            options=self.storage.document_names_mapping,
            multi=True,
            placeholder='Choose documents',
            id='documents-dropdown',
        )

        data_table = html.Div(
            dash_table.DataTable(
                id='data-table',
                columns=[
                    {'name': column, 'id': column}
                    for column in self.storage.columns + ['category']
                ],
                style_table={'overflowX': 'auto'},
                style_header={'textAlign': 'right'},
                style_cell_conditional=[
                    {
                        'if': {'column_id': 'text'},
                        'textAlign': 'left',
                    }
                ],
                style_cell={
                    'height': 'auto',
                    # all three widths are needed
                    'minWidth': '180px',
                    'width': '180px',
                    'maxWidth': '180px',
                    'whiteSpace': 'normal',
                },
            ),
        )

        self.app.layout = html.Div(
            [
                html.Div('Choose categories:'),
                html.Div(
                    categories_div, style={'display': 'flex', 'flex-direction': 'row'}
                ),
                slider,
                html.Div(documents_dropdown, style={'width': '45%', 'margin-top': 10}),
                html.Button(
                    'Categorize documents',
                    id='categorize-button',
                    n_clicks=0,
                    style={'margin-top': 20},
                ),
                html.Hr(),
                html.Div('', id='output-state'),
                data_table,
            ]
        )
        self.add_callbacks()

    def add_callbacks(self):
        self.app.callback(
            Output(
                component_id='approach-to-tax-breakdown-by', component_property='style'
            ),
            Output(
                component_id='approach-to-tax-breakdown-by', component_property='value'
            ),
            Input(component_id='approach-to-tax', component_property='value'),
        )(self.show_breakdown)
        self.app.callback(
            Output(
                component_id='tax-governance-breakdown-by', component_property='style'
            ),
            Output(
                component_id='tax-governance-breakdown-by', component_property='value'
            ),
            Input(component_id='tax-governance', component_property='value'),
        )(self.show_breakdown)
        self.app.callback(
            Output(component_id='approach-to-tax-children', component_property='style'),
            Output(
                component_id='approach-to-tax-children', component_property='options'
            ),
            Input(
                component_id='approach-to-tax-breakdown-by', component_property='value'
            ),
        )(self.show_approach_to_tax_children)
        self.app.callback(
            Output(component_id='tax-governance-children', component_property='style'),
            Output(
                component_id='tax-governance-children', component_property='options'
            ),
            Input(
                component_id='tax-governance-breakdown-by', component_property='value'
            ),
        )(self.show_tax_governance_children)
        self.app.callback(
            Output('approach-to-tax-children', 'value'),
            Input('approach-to-tax-children', 'options'),
        )(self.set_children)
        self.app.callback(
            Output('tax-governance-children', 'value'),
            Input('tax-governance-children', 'options'),
        )(self.set_children)
        self.app.callback(
            Output('output-state', 'children'),
            Output('data-table', 'data'),
            Input('categorize-button', 'n_clicks'),
            State('approach-to-tax', 'value'),
            State('tax-governance', 'value'),
            State('approach-to-tax-children', 'value'),
            State('tax-governance-children', 'value'),
            State('documents-dropdown', 'value'),
            State('threshold', 'value'),
        )(self.categorize_documents)

    def show_breakdown(self, category_selected):
        if category_selected:
            return {
                'display': 'block',
                'position': 'relative',
                'left': 20,
            }, _NO_BREAKDOWN
        return {'display': 'none'}, _NO_BREAKDOWN

    def _get_category_children(
        self, parent_category: str, breakdown_by: str
    ) -> List[str]:
        return self.categories[
            (self.categories.parent_category == parent_category)
            & (self.categories.breakdown_by == breakdown_by)
        ].child_category.tolist()

    def show_approach_to_tax_children(self, breakdown_by):
        if breakdown_by == _NO_BREAKDOWN:
            return {'display': 'none'}, []
        return {
            'display': 'block',
            'position': 'relative',
            'left': 40,
        }, self._get_category_children('approach to tax', breakdown_by)

    def show_tax_governance_children(self, breakdown_by):
        if breakdown_by == _NO_BREAKDOWN:
            return {'display': 'none'}, []
        return {
            'display': 'block',
            'position': 'relative',
            'left': 40,
        }, self._get_category_children('Tax governance', breakdown_by)

    def set_children(self, available_options):
        return available_options

    def categorize_documents(
        self,
        n_clicks,
        approach_to_tax,
        tax_governance,
        approach_to_tax_children,
        tax_governance_children,
        documents_dropdown,
        threshold,
    ):  # pylint: disable=too-many-arguments
        if n_clicks == 0:
            return '', []

        if not documents_dropdown:
            return 'Please, choose documents', []

        categories = []
        if approach_to_tax:
            if approach_to_tax_children:
                categories.extend(approach_to_tax_children)
            else:
                categories.append(approach_to_tax[0])
        if tax_governance:
            if tax_governance_children:
                categories.extend(tax_governance_children)
            else:
                categories.append(tax_governance[0])
        if not categories:
            return 'Please, choose at least one category', []

        data = self.storage.get_data(documents_dropdown).head(10)
        orig_data_len = len(data)

        data = self.categorizer.categorize(data, categories, threshold)
        percent = len(data) / orig_data_len * 100

        return f'{percent:.2f}% of data passed threshold = {threshold}', data.to_dict(
            'records'
        )


if __name__ == '__main__':
    storage = Storage()
    classifier = ZeroShotClassifier()
    categorizer = Categorizer(classifier)

    server = Server(app, storage, categorizer)
    server.app.run_server(debug=True)
