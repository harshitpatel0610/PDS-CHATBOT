import re
from rapidfuzz import fuzz

from .registry import ENTITY_DATA


print(">>> MATCHER.PY LOADED <<<")


class EntityMatcher:


    @staticmethod
    def find(query, entity_type):

        query = query.lower().strip()

        # =====================================================
        # PASS 1: FIND ALL EXACT MATCHES
        # =================================================
# =====================================================
# PASS 1: FIND ALL EXACT MATCHES
# =====================================================

        exact_results = []
        seen = set()

        for item in ENTITY_DATA.get(entity_type, []):

            if isinstance(item, str):
                canonical = item
                search_terms = [item]

            else:
                canonical = item["name"]
                search_terms = [
                    item["name"]
                ] + item.get("aliases", [])

            for term in search_terms:

                term = term.lower().strip()

                # ---------------------------------------------
                # Ignore extremely short entity terms
                # ---------------------------------------------
                if len(term) <= 2:
                    continue

                # ---------------------------------------------
                # Exact whole-word / whole-phrase match
                # ---------------------------------------------
                pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"

                if re.search(pattern, query):

                    normalized = canonical.lower().strip()

                    if normalized not in seen:

                        print(
                            f">>> EXACT MATCH: "
                            f"{query} -> {canonical}"
                        )

                        exact_results.append(
                            (canonical, 100)
                        )

                        seen.add(normalized)

                    break

        # Return ALL exact matches
        if exact_results:
            return exact_results
        # =====================================================
        # PASS 2: FUZZY MATCH
        # =====================================================

        results = []

        for item in ENTITY_DATA.get(entity_type, []):

            if isinstance(item, str):
                canonical = item
                search_terms = [item]

            else:
                canonical = item["name"]
                search_terms = [
                    item["name"]
                ] + item.get("aliases", [])

            best_score = 0

            for term in search_terms:

                term = term.lower().strip()

                # Don't fuzzy-match extremely short terms
                if len(term) <= 2:
                    continue

                score = max(
                    fuzz.token_set_ratio(term, query),
                    fuzz.token_sort_ratio(term, query),
                    fuzz.ratio(term, query)
                )

                best_score = max(
                    best_score,
                    score
                )

            results.append(
                (
                    canonical,
                    best_score
                )
            )

        results.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return results