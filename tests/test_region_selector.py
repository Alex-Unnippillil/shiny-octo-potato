from quiz_automation.region_selector import Region, select_region


def test_region_as_tuple():
    r = Region(1, 2, 3, 4)
    assert r.as_tuple() == (1, 2, 3, 4)


def test_select_region_returns_region():
    r = select_region()
    assert isinstance(r, Region)
