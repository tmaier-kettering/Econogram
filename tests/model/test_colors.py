from scripts.model.colors import ColorAssigner


def test_first_20_colors_are_unique():
    assigner = ColorAssigner()
    colors = [assigner.get_color() for _ in range(20)]
    assert len(set(colors)) == 20


def test_colors_beyond_base_palette_are_still_unique():
    # Exhaust the base tab20 palette (20 colors), then generate 30 more.
    assigner = ColorAssigner()
    colors = [assigner.get_color() for _ in range(50)]
    assert len(set(colors)) == 50, "generated colors collided beyond the base palette"


def test_returned_color_is_reused_before_generating_a_new_one():
    assigner = ColorAssigner()
    first = assigner.get_color()
    assigner.return_color(first)
    second = assigner.get_color()
    assert second == first


def test_return_colors_not_in_use_frees_unused_colors():
    assigner = ColorAssigner()
    a = assigner.get_color()
    b = assigner.get_color()
    assigner.return_colors_not_in_use({a})  # b is no longer in use anywhere
    # b should now be available for reuse
    reused = assigner.get_color()
    assert reused == b


def test_return_colors_not_in_use_with_empty_set_frees_everything():
    assigner = ColorAssigner()
    a = assigner.get_color()
    assigner.return_colors_not_in_use(set())
    assert assigner.get_color() == a


def test_reset_clears_used_colors():
    assigner = ColorAssigner()
    assigner.get_color()
    assigner.reset()
    assert len(assigner.used_colors) == 0
