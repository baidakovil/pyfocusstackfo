-- Focus Stacking Workflow Runner in Terminal
-- This opens Terminal and shows real-time output

on run
	set scriptPath to (path to me as text)
	set workingDir to do shell script "dirname " & quoted form of POSIX path of scriptPath
	
	display notification "Starting focus stacking workflow in Terminal..." with title "PyFocusStackFO"
	
	-- Create the command to run in Terminal
	set terminalCommand to "cd " & quoted form of workingDir & " && source .venv/bin/activate && python main.py"
	
	-- Open Terminal and run the command
	tell application "Terminal"
		activate
		set newTab to do script terminalCommand
		
		-- Optional: Wait for completion and show notification
		repeat
			delay 2
			if not busy of newTab then exit repeat
		end repeat
		
		display notification "Workflow completed! Check Terminal for results." with title "PyFocusStackFO"
	end tell
end run
