import re
from itertools import chain

from src.data.lawbook import LawBook


class ReferencedLookUp:
    def __init__(self, lawbook_data: dict[str, LawBook]):
        self.re_any = re.compile(
            R"((§(und|\s|§|(\d+[a-zA-Z]*)|Abs|\.|Nr|,|satz|S|A|N|u|-)*)\s(\w*))",
            flags=re.IGNORECASE)
        self.re_par_to_par = re.compile(
            R"^(\d+[a-zA-Z]*)(\s+((Abs|A)\.?\s*)+(\d+[a-zA-Z]*)(\s(und|u)\s(\d+[a-zA-Z]*))?)?",
            flags=re.IGNORECASE)
        self.lawbook_data = lawbook_data

    def find_references(self, text: str, book_second_option: str | None = None) -> list[dict]:
        # Get potential references from the text
        references = self._filter_all_possible(text)

        # Filter out, when commentaries are referenced
        references = list(filter(lambda e: e['book'] != 'Rn', references))

        # Split multi-references e.g. §§ 1, 2 Abs. 2, 3 ZPO
        references = self._split_multi_references(references)

        # Split range references e.g. §§ 69-420 BGB
        references = self._split_range_references(references)

        # Get the paragraph and subparagraph numbers
        references = list(chain(*map(self._solve_section_reference, references)))

        # Get the actual laws and filter not found
        references = list(
            filter(None, map(lambda reference: self._lookup_reference(reference, book_second_option), references)))

        references = self._aggregate_duplicates(references)

        references = self._add_ref_names(references)
        return references

    def _add_ref_names(self, references):
        return list(
            map(lambda e: {**e, **{
                'name': f"§ {e['paragraph']}{' Abs. ' if e['subparagraph'] else ''}{e['subparagraph'] if e['subparagraph'] else ''} {e['book']}"}},
                references))

    def _lookup_reference(self, reference: dict, book_second_option: str | None = None) -> dict | None:
        book_name = reference['book'].lower().strip()
        if book_name not in self.lawbook_data.keys() and book_second_option:
            book_name = book_second_option.lower().strip()
        if book_name not in self.lawbook_data.keys():
            return None
        if book_name == book_second_option.lower().strip():
            reference['end']-=len(reference['book'].lower().strip())

        if reference['paragraph'] not in self.lawbook_data[book_name].paragraphs.keys():
            return None

        if reference['subparagraph'] not in self.lawbook_data[book_name] \
                .paragraphs[reference['paragraph']].section_dict.keys():
            return {**reference,
                    **{
                        'text': self.lawbook_data[book_name].paragraphs[
                            reference['paragraph']].section_text_all,
                        'subparagraph': None,
                        'book': self.lawbook_data[book_name].book_name
                    }}
        return {**reference,
                **{
                    'text': self.lawbook_data[book_name].paragraphs[
                        reference['paragraph']].section_dict[reference['subparagraph']],
                    'subparagraph': reference['subparagraph'],
                    'book': self.lawbook_data[book_name].book_name
                }}

    def _solve_section_reference(self, reference: dict) -> list[dict]:
        match = self.re_par_to_par.search(reference['reference'])
        if not match:
            return []

        paragraph, subparagraph, subparagraph2 = match.groups()[0], match.groups()[4], match.groups()[7]

        ref_info = {key: reference[key] for key in ['begin', 'end', 'book']}

        ret = [{**ref_info, 'paragraph': paragraph, 'subparagraph': subparagraph}]

        if subparagraph2:
            ret.append({**ref_info, 'paragraph': paragraph, 'subparagraph': subparagraph2})

        return ret

    # noinspection PyMethodMayBeStatic
    def _split_range_references(self, references: list[dict]) -> list[dict]:
        references2 = []
        for reference in references:
            start_end = reference['reference'].replace(' ', '').split('-')
            if len(start_end) == 2 and start_end[0].isdigit() and start_end[1].isdigit():
                for ref_num in range(int(start_end[0]), int(start_end[1])):
                    references2.append({**reference, **{'reference': str(ref_num)}})
            else:
                references2.append(reference)
        return references2

    # noinspection PyMethodMayBeStatic
    def _split_multi_references(self, references: list[dict]) -> list[dict]:
        return [
            {**reference, **{'reference': ref_part.strip()}}
            for reference in references
            for ref_part in reference['reference'].split(',')
        ]

    # noinspection PyMethodMayBeStatic
    def _aggregate_duplicates(self, references: list[dict]) -> list[dict]:
        references_agg = {}
        for reference in references:
            key = (reference['book'].lower(), reference['paragraph'], reference['subparagraph'])
            if key not in references_agg.keys():
                references_agg[key] = {**reference, **{'begin': [], 'end': []}}
            references_agg[key]['begin'].append(reference['begin'])
            references_agg[key]['end'].append(reference['end'])

        for reference in references_agg.values():
            reference['begin'] = sorted(list(set(reference['begin'])))
            reference['end'] = sorted(list(set(reference['end'])))

        return list(references_agg.values())

    def _filter_all_possible(self, text: str) -> list[dict]:
        references_found = []
        regex_found = self.re_any.finditer(text)
        for reference in regex_found:
            references_found.append({
                'begin': reference.start(),
                'end': reference.end(),
                'original': reference.groups()[0],
                'reference': reference.groups()[1].strip().strip('§'),
                'book': reference.groups()[4].strip(),
            })
        return references_found
