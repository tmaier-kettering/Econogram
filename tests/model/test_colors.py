from scripts.model.colors import ColorAssigner
import matplotlib.colors as mcolors


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


def test_generate_new_color_retries_on_collision():
    """Verify the collision-retry path in _generate_new_color actually executes.

    This test forces a real collision by pre-seeding used_colors with the exact
    color the fallback generator would naively produce for attempt=0, then
    verifies the retry loop correctly returns a different color.
    """
    assigner = ColorAssigner()

    # Exhaust the base tab20 palette (20 colors)
    for _ in range(20):
        assigner.get_color()

    # Calculate what the first generated color would be (attempt=0).
    # When available_colors is empty and _generate_new_color is called:
    # attempt = len(used_colors) - len(base_colors) = 20 - 20 = 0
    hue = (0 * 0.618033988749895) % 1.0      # = 0.0
    saturation = 0.6 + (0 % 3) * 0.15        # = 0.6
    value = 0.7 + (0 % 2) * 0.2              # = 0.7
    first_generated = tuple(mcolors.hsv_to_rgb([hue, saturation, value]))

    # Pre-seed this exact color as already used (simulating a collision)
    assigner.used_colors.add(first_generated)

    # Now call get_color() and verify the retry loop returns a different color
    returned_color = assigner.get_color()

    # Assert the retry worked: returned color is NOT the pre-seeded collision
    assert returned_color != first_generated, \
        f"Expected retry to find different color, but got {returned_color} (collision color)"

    # Assert the returned color is valid and now in used_colors
    assert len(returned_color) == 3, "Returned value should be an RGB tuple"
    assert all(0 <= c <= 1 for c in returned_color), "RGB values should be in [0, 1]"
    assert returned_color in assigner.used_colors, "Returned color should be in used_colors"
