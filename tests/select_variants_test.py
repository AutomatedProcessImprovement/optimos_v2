from o2.models.settings import ActionVariationSelection
from o2.store import Store
from o2.util.helper import select_variants


def test_select_variants_simple(one_task_store: Store):
    settings = one_task_store.settings
    settings.max_variants_per_action = 2
    options = [1, 2, 3, 4, 5]

    settings.action_variation_selection = ActionVariationSelection.FIRST_IN_ORDER
    assert list(select_variants(one_task_store, options)) == [1]

    settings.action_variation_selection = ActionVariationSelection.FIRST_MAX_VARIANTS_PER_ACTION_IN_ORDER
    assert list(select_variants(one_task_store, options)) == [1, 2]

    settings.action_variation_selection = ActionVariationSelection.RANDOM_MAX_VARIANTS_PER_ACTION
    assert len(list(select_variants(one_task_store, options))) == 2

    settings.action_variation_selection = ActionVariationSelection.ALL_RANDOM
    assert sorted(select_variants(one_task_store, options)) == options

    settings.action_variation_selection = ActionVariationSelection.ALL_IN_ORDER
    assert list(select_variants(one_task_store, options)) == options

    settings.action_variation_selection = ActionVariationSelection.SINGLE_RANDOM
    assert len(list(select_variants(one_task_store, options))) == 1


def test_select_variants_inner(one_task_store: Store):
    settings = one_task_store.settings
    settings.max_variants_per_action = 2

    options = [1, 2, 3, 4, 5]

    settings.action_variation_selection = ActionVariationSelection.FIRST_IN_ORDER
    assert list(select_variants(one_task_store, options, inner=True)) == [1]

    settings.action_variation_selection = ActionVariationSelection.FIRST_MAX_VARIANTS_PER_ACTION_IN_ORDER
    assert list(select_variants(one_task_store, options, inner=True)) == [1]

    settings.action_variation_selection = ActionVariationSelection.RANDOM_MAX_VARIANTS_PER_ACTION
    assert len(list(select_variants(one_task_store, options, inner=True))) == 1

    settings.action_variation_selection = ActionVariationSelection.ALL_RANDOM
    assert len(list(select_variants(one_task_store, options, inner=True))) == 1

    settings.action_variation_selection = ActionVariationSelection.ALL_IN_ORDER
    assert list(select_variants(one_task_store, options, inner=True)) == [1]

    settings.action_variation_selection = ActionVariationSelection.SINGLE_RANDOM
    assert len(list(select_variants(one_task_store, options, inner=True))) == 1


def test_select_variants_ordered(one_task_store: Store):
    settings = one_task_store.settings
    settings.max_variants_per_action = 2

    options = [1, 2, 3, 4, 5]

    settings.action_variation_selection = ActionVariationSelection.FIRST_IN_ORDER
    assert list(select_variants(one_task_store, options, ordered=True)) == [1]

    settings.action_variation_selection = ActionVariationSelection.FIRST_MAX_VARIANTS_PER_ACTION_IN_ORDER
    assert list(select_variants(one_task_store, options, ordered=True)) == [1, 2]

    settings.action_variation_selection = ActionVariationSelection.RANDOM_MAX_VARIANTS_PER_ACTION
    assert list(select_variants(one_task_store, options, ordered=True)) == [1, 2]

    settings.action_variation_selection = ActionVariationSelection.ALL_RANDOM
    assert list(select_variants(one_task_store, options, ordered=True)) == options

    settings.action_variation_selection = ActionVariationSelection.ALL_IN_ORDER
    assert list(select_variants(one_task_store, options, ordered=True)) == options

    settings.action_variation_selection = ActionVariationSelection.SINGLE_RANDOM
    assert list(select_variants(one_task_store, options, ordered=True)) == [1]


def test_select_variants_inner_ordered(one_task_store: Store):
    settings = one_task_store.settings
    settings.max_variants_per_action = 2

    options = [1, 2, 3, 4, 5]

    settings.action_variation_selection = ActionVariationSelection.FIRST_IN_ORDER
    assert list(select_variants(one_task_store, options, inner=True, ordered=True)) == [1]

    settings.action_variation_selection = ActionVariationSelection.FIRST_MAX_VARIANTS_PER_ACTION_IN_ORDER
    assert list(select_variants(one_task_store, options, inner=True, ordered=True)) == [1]

    settings.action_variation_selection = ActionVariationSelection.RANDOM_MAX_VARIANTS_PER_ACTION
    assert list(select_variants(one_task_store, options, inner=True, ordered=True)) == [1]

    settings.action_variation_selection = ActionVariationSelection.ALL_RANDOM
    assert list(select_variants(one_task_store, options, inner=True, ordered=True)) == [1]

    settings.action_variation_selection = ActionVariationSelection.ALL_IN_ORDER
    assert list(select_variants(one_task_store, options, inner=True, ordered=True)) == [1]

    settings.action_variation_selection = ActionVariationSelection.SINGLE_RANDOM
    assert list(select_variants(one_task_store, options, inner=True, ordered=True)) == [1]
