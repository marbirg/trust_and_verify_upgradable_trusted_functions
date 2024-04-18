

import os
import subprocess

print("Hello world from python")

# Command to echo 'Hello, World!'
# command = "echo Hello, World! from system"
command = "/usr/lib/dafny/dafny /version"

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
print(output)


