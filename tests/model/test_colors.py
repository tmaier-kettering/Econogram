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

    _generate_new_color computes attempt = len(used_colors) - len(base_colors).
    Seeding a color directly into used_colors (to simulate a collision) itself
    increases len(used_colors) by 1 -- so to force a collision on the very
    first candidate the generator checks, we must seed the candidate for
    attempt=1 (not attempt=0): after exhausting the base palette,
    len(used_colors) == 20, and adding one seeded color makes it 21, so the
    first candidate _generate_new_color actually evaluates is for
    attempt = 21 - 20 = 1. Seeding that exact color forces a genuine
    collision, so the retry loop must advance to attempt=2 to find a free
    color.
    """
    assigner = ColorAssigner()

    # Exhaust the base tab20 palette (20 colors)
    for _ in range(20):
        assigner.get_color()

    # Candidate the generator would check for attempt=1 -- this is the color
    # that will actually be evaluated first once our seed is counted.
    hue = (1 * 0.618033988749895) % 1.0
    saturation = 0.6 + (1 % 3) * 0.15
    value = 0.7 + (1 % 2) * 0.2
    attempt_1_candidate = tuple(mcolors.hsv_to_rgb([hue, saturation, value]))

    # Candidate the generator should fall back to on retry (attempt=2),
    # proving the loop actually advanced rather than coincidentally differing.
    hue = (2 * 0.618033988749895) % 1.0
    saturation = 0.6 + (2 % 3) * 0.15
    value = 0.7 + (2 % 2) * 0.2
    attempt_2_candidate = tuple(mcolors.hsv_to_rgb([hue, saturation, value]))

    # Pre-seed the attempt=1 candidate as already used (simulating a collision)
    assigner.used_colors.add(attempt_1_candidate)

    # Now call get_color() and verify the retry loop returns a different color
    returned_color = assigner.get_color()

    # Assert the retry worked: returned color is NOT the pre-seeded collision
    assert returned_color != attempt_1_candidate, \
        f"Expected retry to find different color, but got {returned_color} (collision color)"

    # Assert the loop landed on the correct fallback (attempt=2), proving it
    # advanced exactly one step rather than jumping to an arbitrary color.
    assert returned_color == attempt_2_candidate, \
        f"Expected retry to fall back to attempt=2 candidate {attempt_2_candidate}, got {returned_color}"

    # Assert the returned color is valid and now in used_colors
    assert len(returned_color) == 3, "Returned value should be an RGB tuple"
    assert all(0 <= c <= 1 for c in returned_color), "RGB values should be in [0, 1]"
    assert returned_color in assigner.used_colors, "Returned color should be in used_colors"
