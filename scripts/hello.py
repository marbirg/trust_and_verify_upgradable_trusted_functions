

import os
import subprocess

print("Hello world from python")

# Command to echo 'Hello, World!'
# command = "echo Hello, World! from system"
# command = "/usr/lib/dafny/dafny /version"
# command = "/usr/lib/dafny/dafny verify scripts/Max.dfy /compileTarget:py /out:/data/"
# command = "/usr/lib/dafny/dafny verify scripts/Max.dfy /compileTarget:py"
# command = "/usr/lib/dafny/dafny verify scripts/Max.dfy"
# command = "/usr/lib/dafny/dafny scripts/Max.dfy /out:/data/Max /compileTarget:py"
command = "/usr/lib/dafny/dafny scripts/Max.dfy /out:/scripts/maxlib /compileTarget:py"
# command = "/usr/lib/dafny/dafny verify scripts/Abs.dfy"

# Open a pipe to the command
# pipe = os.popen(command)
# pipe = os.popen(command)
# output = subprocess.Popen(['/usr/bin/bash','-c', command])
output = subprocess.check_output(['/usr/bin/bash','-c', command])
output=output.decode('utf8')
# Read the output of the command
# output = pipe.read()

# Close the pipe
# pipe.close()

# Print the output
print("Command:", command)
print("Result:",output)


