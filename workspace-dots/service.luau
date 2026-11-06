-- One event stream for every bar; no polling and no per-monitor caches.
local path = noctalia.pluginDir() .. "/workspace_state.py"
local command = "exec python3 -u '" .. string.gsub(path, "'", "'\\''") .. "'"
local started = noctalia.runStream(command, function(line)
  local snapshot, err = noctalia.json.decode(line)
  if snapshot then
    noctalia.state.set("workspaces", snapshot)
    if snapshot.error then noctalia.log(snapshot.error) end
  else
    noctalia.log("Invalid workspace snapshot: " .. tostring(err))
  end
end)
if not started then
  noctalia.state.set("workspaces", { error = "Could not start the Hyprland workspace reader" })
end
