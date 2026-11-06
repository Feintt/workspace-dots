import unittest

from workspace_state import workspace_states


def workspace(number, windows=0, monitor="HDMI-A-1"):
    return {"id": number, "type": "normal", "windows": windows, "monitor": monitor}


class WorkspaceStateTests(unittest.TestCase):
    def test_empty_other_monitor_never_looks_occupied(self):
        workspaces = [workspace(8, monitor="eDP-1"), workspace(2, windows=1)]
        self.assertEqual(workspace_states(workspaces, workspaces[1])["dots"],
                         ["empty", "focused", "empty", "empty", "empty", "empty", "empty", "empty"])
        self.assertEqual(workspace_states(workspaces, workspaces[0])["dots"],
                         ["empty", "occupied", "empty", "empty", "empty", "empty", "empty", "focused"])

    def test_last_window_closing_clears_previous_occupancy(self):
        active = workspace(3)
        self.assertEqual(workspace_states([workspace(1, windows=1), active], active)["dots"][0], "occupied")
        self.assertEqual(workspace_states([workspace(1), active], active)["dots"][0], "empty")

    def test_hotplug_reordering_does_not_change_dot_identity(self):
        before = [workspace(8, monitor="eDP-1"), workspace(2, windows=1)]
        after = [workspace(2, windows=1, monitor="eDP-1"), workspace(8, monitor="eDP-1")]
        expected = ["empty", "occupied", "empty", "empty", "empty", "empty", "empty", "focused"]
        self.assertEqual(workspace_states(before, before[0])["dots"], expected)
        self.assertEqual(workspace_states(after, after[1])["dots"], expected)

    def test_named_special_and_out_of_range_workspaces_cannot_shift_slots(self):
        named = {"type": "normal", "name": "4", "windows": 2}
        special = {"type": "special", "id": 3, "windows": 1}
        workspaces = [named, special, workspace(9, windows=1), workspace(4, windows=1)]
        self.assertEqual(workspace_states(workspaces, named)["dots"],
                         ["empty", "empty", "empty", "occupied", "empty", "empty", "empty", "empty"])


if __name__ == "__main__":
    unittest.main()
