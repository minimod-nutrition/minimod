from tabulate import tabulate


class Summary:

    def __init__(self, model, table_fmt = "psql", decimals = 3, **kwargs):

        self.model = model
        self.table_fmt = table_fmt
        self.decimals = decimals

        if model.opt_df is not None:
            self.opt_df = model.opt_df
        else:
            raise Exception("Results from fit not found. Did you run the fit method before summarizing?")

    def _print_specific_style(self, style, data):
        if style == "html":
            return self.html_print(data)
        elif style == "markdown":
            return self.markdown_print(data)
        elif style == "latex":
            return self.latex_print(data)
        elif style == 'pandas':
            return self.pandas_show(data)
        else:
            raise ValueError("style not available.")

    @staticmethod
    def html_print(data):

        return print(data.to_html())

    @staticmethod
    def markdown_print(data):
        return print(data.to_markdown())

    @staticmethod
    def latex_print(data):
        return print(data.to_latex())

    @staticmethod
    def pandas_show(data):
        return print(data)

    def _sum_of_all(self,
                    intervention_specific=None,
                    col='costs'):

        if intervention_specific is None:
            intervention_specific = slice(None)

        sum_ = (self.opt_df[col]
                    .loc[(intervention_specific, slice(None), slice(None)), :]).sum()
        return sum_

    def _group_summarizer(self,
                          intervention_specific=None,
                          over_time=True,
                          across_space=False,
                          style=None):

        if style is None:
            print("[Note]: style not specified, printing as pandas dataframe")
            print_style = self.pandas_show
        if style is not None:
            print_style = self._print_specific_style

        grouper = []

        if intervention_specific is None:
            intervention_specific = slice(None)

        if across_space:
            grouper.append(self.model._space)

        if over_time:
            grouper.append(self.model._time)

        summary_data = (self.opt_df
                        .loc[(intervention_specific, slice(None), slice(None)), :]
                        .groupby(grouper)
                        .sum())

        return print_style(style, summary_data)

    def _report(self):
        
        header = [
            ('MiniMod Solver Results', ""),
            ("Method:" , str(self.model.sense)),
            ("Solver:", str(self.model.solver_name)),
            ("Optimization Status:", str(self.model.status)),
            ("Number of Solutions Found:", str(self.model.model.num_solutions))

        ]

        print(tabulate(header, tablefmt=self.table_fmt))

        features = [
            ("No. of Variables:", str(self.model.model.num_cols)),
            ("No. of Integer Variables:", str(self.model.model.num_int)),
            ("No. of Constraints", str(self.model.model.num_rows)),
            ("No. of Non-zeros in Constr.", str(self.model.model.num_nz))
            ]

        print(tabulate(features, tablefmt=self.table_fmt))

        if hasattr(self.model, "minimum_benefit"):
            ms_str = "Minimum Benefit"
            ms_num = self.model.minimum_benefit
            total_benefits = self.model.model.objective_value
            total_costs = self.model.model.objective_bound
        elif hasattr(self.model, "total_funds"):
            ms_str = "Total Funds"
            ms_num = self.model.total_funds
            total_benefits = self.model.model.objective_bound
            total_costs = self.model.model.objective_value

        results = [
            (ms_str, ms_num),
            ("Total Cost", total_costs ),
            ("Total Coverage", total_benefits)
        ]

        print(tabulate(results, tablefmt=self.table_fmt))
        print(tabulate([("Total Costs and Coverage by Year", "")], tablefmt=self.table_fmt))
        self._group_summarizer(over_time=True, style='markdown')
        print(tabulate([("Cost per Coverage", total_costs / total_benefits)], tablefmt=self.table_fmt))



