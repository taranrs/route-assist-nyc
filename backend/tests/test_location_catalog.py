import unittest

from app.services.location_catalog import (
    canonical_location_name,
    get_demo_location_names,
    resolve_demo_location,
)


class LocationCatalogTests(unittest.TestCase):
    def test_lowercase_input_matching(self):
        self.assertEqual(canonical_location_name("times square"), "Times Square")

    def test_alias_matching(self):
        self.assertEqual(canonical_location_name("time square"), "Times Square")
        self.assertEqual(canonical_location_name("penn"), "Penn Station")
        self.assertEqual(canonical_location_name("nyu"), "Washington Square Park")
        self.assertEqual(canonical_location_name("wall st"), "Wall Street")

    def test_catalog_contains_demo_coordinates(self):
        location = resolve_demo_location("wtc")

        self.assertIsNotNone(location)
        self.assertEqual(location.display_name, "World Trade Center")
        self.assertIsInstance(location.latitude, float)
        self.assertIsInstance(location.longitude, float)

    def test_location_catalog_helper_returns_known_demo_locations(self):
        names = get_demo_location_names()

        self.assertIn("Empire State Building", names)
        self.assertIn("Central Park South", names)
        self.assertIn("Battery Park", names)


if __name__ == "__main__":
    unittest.main()
