import random
from math import comb
from itertools import combinations
from typing import Any

from src.types import JSON


class HtmlConfigurator:
    def __init__(
        self,
        invoices_used: list[int],
        templates_used: list[int],
        specific_product_nums: list[int],
        languages_used: list[str] | None = None,
    ):
        """
        :param invoices_used: Number of different invoices
        :param templates_used: Number of different templates
        :param specific_product_nums: list with the lowest and highest number of products that are allowed to appear
                                      in the invoices.
        :param languages_used: Number of languages in which the invoices are written.
                                24.06.2024: Not yet clear how the languages will be implemented.
                                            Current approach is to take German content and run it through Google
                                            Translate for all other languages?
        """
        self.invoices_used = invoices_used
        self.templates_used = templates_used
        self.specific_product_nums = specific_product_nums
        self.languages_used = languages_used

    def calculate_html_number(self) -> int:
        """
        Calculates the final number of HTMLs that will be created based on the parameters passed.

        :return:
        """
        # n over k like lotto 10 over [list of numbers within the selected range]
        # e.g. 10 over 2 = 45, 10 over 10 = 1, 10 over 1 = 10, 10 over 5 = 252
        # Covers all possible combinations.
        product_combinations = [comb(10, int(num)) for num in self.specific_product_nums]
        languages_count = len(self.languages_used) if self.languages_used is not None else 1
        html_count: int = (
            len(self.invoices_used)
            * len(self.templates_used)
            * languages_count
            * sum(product_combinations)
        )
        return html_count

    def detailed_combinations(self) -> list[JSON]:
        """
        Detailed breakdown of the various combinations available.
        Used to dynamically modify the invoice content in order to create the invoices.

        :return: List with a detailed breakdown of the combinatorics, including the minimum and maximum
                 number of products
        """
        all_combinations = [
            entry
            for combination in [
                list(combinations(range(1, 11), int(num))) for num in self.specific_product_nums
            ]
            for entry in combination
        ]

        lists_with_detailed_combs = []
        for combi in all_combinations:
            for invoice in self.invoices_used:
                for template in self.templates_used:
                    lists_with_detailed_combs.append(
                        {
                            "templateID": template,
                            "invoiceID": invoice,
                            "productsToUse": combi,
                        }
                    )
        return lists_with_detailed_combs

    def detailed_combinations_restricted(self, max_invoices: int = 50) -> list[JSON]:
        """
        Detailed breakdown of the different combinations available, used to dynamically modify the invoice content
        in order to create the invoices.

        :return: List with a detailed breakdown of the combinatorics, including the minimum and maximum
                 number of products
        """
        # return list
        lists_with_detailed_combs: list[JSON] = []
        all_combinations: list[tuple[int, ...]] = []
        # calculate the possible combinations for the specific product number and sort it by length (aufsteigend)
        possible_combinations: list[list[tuple[int, ...]]] = sorted(
            [
                combination
                for combination in [
                    list(combinations(range(1, 11), int(num))) for num in self.specific_product_nums
                ]
            ],
            key=len,
        )

        # calculate the maximum share that each product number receives

        share_per_product: list[int] = self.distribute_evenly(
            total=max_invoices, parts=len(possible_combinations), shuffle=True
        )
        # check if all combos are below or equal the share
        all_below_or_equal_share = all(
            [
                len(combo) <= share_per_product[index]
                for index, combo in enumerate(possible_combinations)
            ]
        )
        # check if the sum of the combinations is below max_invoices
        sum_below_max_invoices = sum([len(combo) for combo in possible_combinations]) < max_invoices

        if all_below_or_equal_share and not sum_below_max_invoices:
            index_to_drop: list[int] = []
            new_max_after_appending_smaller_nums: int
            for index, combo in enumerate(possible_combinations):
                if len(combo) <= share_per_product[index]:
                    for entry in combo:
                        all_combinations.append(entry)
                        index_to_drop.append(index)
            for index in reversed(
                list(set(index_to_drop))
            ):  # set-list removes duplicates in indexes
                possible_combinations.pop(index)
            # calculate the new max_invoices which remain after appending the other combinations
            max_invoices = max_invoices - len(all_combinations)
            # calculate the new share per remaining product numbers and shuffle
            share_per_product = self.distribute_evenly(
                total=max_invoices, parts=len(possible_combinations), shuffle=True
            )
        # process the rest which are bigger then the max share or if the sum of the combos is below max_invoices
        for index, rest_combos in enumerate(possible_combinations):
            # pick random samples from the combinations

            if share_per_product[index] < len(rest_combos):  # share_bigger_then_combos ?
                random_entries = random.sample(rest_combos, share_per_product[index])
            else:
                random_entries = rest_combos
            for entry in random_entries:
                all_combinations.append(entry)

        for combi in all_combinations:
            for invoice in self.invoices_used:
                for template in self.templates_used:
                    lists_with_detailed_combs.append(
                        {
                            "templateID": template,
                            "invoiceID": invoice,
                            "productsToUse": combi,
                        }
                    )
        return lists_with_detailed_combs

    @staticmethod
    def distribute_evenly(total: int, parts: int, shuffle: bool) -> list[int]:
        """
        Calculation of even numbers after a division that resulted in decimal numbers:
        Example: 50/3 = 16.666...8 -> Not usable if you want to  use it to say that X things must be taken.
        Goal: To find the combination of integer values that is closest to reality.
        For 50/3 this would be the numbers 16,17,17.


        :param total: Maximum Number
        :param parts:  How many parts are split into
        :param shuffle: Should be shuffled again at the end
        :return: List of integer values that are closest to the decimal point distribution.
        :rtype:
        """
        # Basic value for each part
        base_value = total // parts

        # Remainder to be distributed
        remainder = total % parts

        # Create the parts with the basic value
        # If only 1 is picked skip the * parts because remainder will be 0 -> error
        result = [base_value] * parts  # if total % parts > 0 else [base_value]

        # Add the rest evenly to the first 'remainder' parts
        for i in range(remainder):
            result[i] += 1
        if len(result) > 1 and shuffle:
            random.shuffle(result)
        return result


def main():
    from pprint import pprint

    templates = [1, 2, 3]
    invoices = [12, 13, 14]
    languages = ["german"]
    spec_nums = [1, 4, 6, 5, 8, 9]
    configurator = HtmlConfigurator(
        templates_used=templates,
        invoices_used=invoices,
        languages_used=languages,
        specific_product_nums=spec_nums,
    )
    detialed_infos = configurator.detailed_combinations_restricted()
    pprint(detialed_infos)


if __name__ == "__main__":
    main()
