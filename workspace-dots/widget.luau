-- All bars show the same global IDs. Focus is not evidence of window occupancy.
local snapshot = nil
local colors = { focused = "primary", occupied = "secondary", empty = "outline_variant" }

local function render()
  local dots = {}
  for number = 1, 8 do
    local state = snapshot and snapshot.dots and snapshot.dots[number]
    local description = state or (snapshot and snapshot.error) or "Loading workspace state"
    dots[number] = ui.row({
      key = tostring(number),
      width = 20,
      height = 24,
      align = "center",
      justify = "center",
      tooltip = "Workspace " .. tostring(number) .. ": " .. description,
      onClick = function()
        local command = string.format("hl.dispatch(hl.dsp.focus({ workspace = %d }))", number)
        noctalia.runAsync({ "hyprctl", "eval", command })
      end,
    }, {
      ui.box({
        width = state == "focused" and 12 or 10,
        height = state == "focused" and 12 or 10,
        radius = 6,
        fill = colors[state] or "outline_variant/0.5",
      }),
    })
  end
  local container = barWidget.isVertical() and ui.column or ui.row
  barWidget.render(container({ align = "center" }, dots))
end

noctalia.state.watch("workspaces", function(value)
  snapshot = value
  render()
end)
snapshot = noctalia.state.get("workspaces")
render()
