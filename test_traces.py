import unittest

import numpy as np
import plotly.graph_objects as go
from constants import DEFAULT_VEHICLE_COLOR, DEFAULT_VEHICLE_STYLES
from globe import FlightGlobeAnimator


class TestTraceCreation(unittest.TestCase):
    """Unit tests for FlightGlobeAnimator trace creation methods."""

    def setUp(self):
        """Set up test fixtures with mock data."""

        # print()
        # print("=" * 50)
        # print("Initializing FlightGlobeAnimator tests...")
        # print("=" * 50)

        # Mock flights data for testing
        self.mock_flights = [
            {
                "source": {"lat": 40.7128, "lng": -74.0060, "city": "New York"},
                "target": {"lat": 51.5074, "lng": -0.1278, "city": "London"},
                "date": "2024-01-01",
                "vehicle": "plane",
            }
        ]

        # Mock great circle function for testing
        def mock_great_circle(lat1, lon1, lat2, lon2, num_points):
            lats = np.linspace(lat1, lat2, num_points)
            lons = np.linspace(lon1, lon2, num_points)
            return lats, lons

        # Create animator instance
        self.animator = FlightGlobeAnimator(
            self.mock_flights, mock_great_circle, verbose=False
        )

    def test_create_path_trace(self):
        """Test path trace creation with different vehicles and parameters."""
        # Test data
        lats = np.array([40.7128, 45.0, 51.5074])
        lons = np.array([-74.0060, -37.0, -0.1278])

        # Test with known vehicle
        trace = self.animator._create_path_trace(lats, lons, "plane", 3, 0)

        # Assertions
        self.assertIsInstance(trace, go.Scattergeo)
        self.assertEqual(trace.mode, "lines")
        self.assertEqual(trace.line.width, 3)
        self.assertNotEqual(trace.line.color, DEFAULT_VEHICLE_STYLES["plane"]["color"])
        self.assertTrue(trace.showlegend)
        self.assertEqual(trace.hoverinfo, "skip")
        self.assertEqual(trace.name, "Plane path")
        np.testing.assert_array_equal(trace.lat, lats)
        np.testing.assert_array_equal(trace.lon, lons)

    def test_create_marker_trace_source(self):
        """Test source marker trace creation."""
        trace = self.animator._create_marker_trace(
            40.7128, -74.0060, "New York", "plane"
        )

        # Assertions
        self.assertIsInstance(trace, go.Scattergeo)
        self.assertEqual(trace.mode, "markers+text")
        self.assertEqual(list(trace.lat), [40.7128])
        self.assertEqual(list(trace.lon), [-74.0060])
        self.assertEqual(list(trace.text), ["New York"])
        self.assertEqual(trace.textposition, "top center")
        self.assertTrue(trace.showlegend)
        self.assertEqual(trace.hoverinfo, "text")
        self.assertEqual(list(trace.hovertext), ["City New York"])
        self.assertEqual(trace.name, "City New York")

        # Check marker properties
        self.assertEqual(trace.marker.size, 12)
        self.assertEqual(trace.marker.color, "white")
        self.assertEqual(trace.marker.line.width, 2)
        self.assertEqual(
            trace.marker.line.color, DEFAULT_VEHICLE_STYLES["plane"]["color"]
        )

    def test_create_marker_trace_destination(self):
        """
        Test destination marker trace creation.
        """

        trace = self.animator._create_marker_trace(51.5074, -0.1278, "London", "train")

        # Assertions
        # print(trace)

        self.assertEqual(list(trace.lat), [51.5074])
        self.assertEqual(list(trace.lon), [-0.1278])
        self.assertEqual(list(trace.text), ["London"])
        self.assertEqual(list(trace.hovertext), ["City London"])
        self.assertEqual(trace.name, "City London")
        self.assertEqual(
            trace.marker.line.color, DEFAULT_VEHICLE_STYLES["train"]["color"]
        )

    def test_create_moving_point_trace(self):
        """Test moving point trace creation."""
        trace = self.animator._create_moving_point_trace(45.0, -37.0, "car")

        # Assertions
        self.assertIsInstance(trace, go.Scattergeo)
        self.assertEqual(trace.mode, "markers+text")
        self.assertEqual(list(trace.lat), [45.0])
        self.assertEqual(list(trace.lon), [-37.0])
        self.assertEqual(list(trace.text), [DEFAULT_VEHICLE_STYLES["car"]["icon"]])
        self.assertEqual(trace.textposition, "middle center")
        self.assertTrue(trace.showlegend)
        self.assertEqual(trace.hoverinfo, "text")
        self.assertEqual(list(trace.hovertext), ["Traveling by car"])
        self.assertEqual(trace.name, "Moving By car")

        # Check marker properties
        self.assertEqual(trace.marker.size, 15)
        self.assertEqual(trace.marker.color, DEFAULT_VEHICLE_STYLES["car"]["color"])
        self.assertEqual(trace.textfont.size, 20)

    def test_create_moving_point_trace_unknown_vehicle(self):
        """Test moving point trace with unknown vehicle type."""
        trace = self.animator._create_moving_point_trace(45.0, -37.0, "spaceship")

        # Should fall back to default style
        self.assertEqual(list(trace.text), [DEFAULT_VEHICLE_STYLES["default"]["icon"]])
        self.assertEqual(trace.marker.color, DEFAULT_VEHICLE_STYLES["default"]["color"])
        self.assertEqual(trace.name, "Moving By spaceship")


class TestTraceIntegration(unittest.TestCase):
    """Integration tests for trace creation and frame updates."""

    def setUp(self):
        """Set up test fixtures for integration testing."""
        self.mock_flights = [
            {
                "source": {"lat": 40.7128, "lng": -74.0060, "city": "New York"},
                "target": {"lat": 51.5074, "lng": -0.1278, "city": "London"},
                "date": "2024-01-01",
                "vehicle": "plane",
            }
        ]

        def mock_great_circle(lat1, lon1, lat2, lon2, num_points):
            lats = np.linspace(lat1, lat2, num_points)
            lons = np.linspace(lon1, lon2, num_points)
            return lats, lons

        self.animator = FlightGlobeAnimator(
            self.mock_flights,
            mock_great_circle,
            config={"total_frames": 20, "points_per_flight": 10},
        )

    def test_frame_data_consistency(self):
        """Test that all traces are properly created and maintain consistency."""
        # Generate a few frames
        frame_0 = self.animator._generate_frame(0)
        frame_5 = self.animator._generate_frame(5)
        frame_15 = self.animator._generate_frame(15)

        # Check that frames contain data
        self.assertGreater(len(frame_0.data), 0)
        self.assertGreater(len(frame_5.data), 0)
        self.assertGreater(len(frame_15.data), 0)

        # Check frame names
        self.assertEqual(frame_0.name, "frame_0")
        self.assertEqual(frame_5.name, "frame_5")
        self.assertEqual(frame_15.name, "frame_15")

    def test_trace_types_in_frames(self):
        """Test that frames contain the expected types of traces."""
        frame = self.animator._generate_frame(10)

        # Check that all traces are Scattergeo objects
        for trace in frame.data:
            self.assertIsInstance(trace, go.Scattergeo)

        # Check for expected trace names patterns
        trace_names = [trace.name for trace in frame.data]
        print(f"Trace names in frame 10: {trace_names}")

        # Should have at least one of each type by frame 10
        has_text = any("City" in name for name in trace_names)
        has_path = any("path" in name for name in trace_names)
        has_moving = any("Moving By" in name for name in trace_names)

        self.assertTrue(has_text, f"No text found in traces: {trace_names}")
        self.assertTrue(has_path, f"No path trace found in traces: {trace_names}")
        self.assertTrue(has_moving, f"No moving point found in traces: {trace_names}")

    def test_coordinate_bounds(self):
        """Test that all coordinates are within valid ranges."""
        frame = self.animator._generate_frame(10)

        for trace in frame.data:
            # print(type(trace.lat))

            # Check latitude bounds (-90 to 90)
            if hasattr(trace, "lat") and trace.lat:
                for lat in trace.lat:
                    self.assertGreaterEqual(lat, -90)
                    self.assertLessEqual(lat, 90)

            # Check longitude bounds (-180 to 180)
            if hasattr(trace, "lon") and trace.lon:
                for lon in trace.lon:
                    self.assertGreaterEqual(lon, -180)
                    self.assertLessEqual(lon, 180)

    def test_simultaneous_display(self):
        """Test that multiple traces can be displayed simultaneously."""
        frame = self.animator._generate_frame(15)

        # Should have multiple traces that can be displayed together
        self.assertGreater(len(frame.data), 1)

        # All traces should be compatible for simultaneous display
        for trace in frame.data:
            # Check that essential properties exist
            self.assertTrue(hasattr(trace, "lat"))
            self.assertTrue(hasattr(trace, "lon"))
            self.assertTrue(hasattr(trace, "mode"))
            self.assertTrue(hasattr(trace, "name"))

            # Check that traces have valid modes
            valid_modes = ["lines", "markers", "markers+text", "lines+markers"]
            self.assertIn(trace.mode, valid_modes)

    def test_show_fig(self):
        fig = self.animator.create_animation()
        fig.show()


if __name__ == "__main__":
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases using TestLoader (no deprecation warning)
    suite.addTest(loader.loadTestsFromTestCase(TestTraceCreation))
    suite.addTest(loader.loadTestsFromTestCase(TestTraceIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print()
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(
        f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%"
    )
    print(f"{'='*50}")
