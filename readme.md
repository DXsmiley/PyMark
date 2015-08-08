# PyMark Code Judge

Marking student's code is difficult and time consuming, and while there are many code judges online, they are all closed and often difficult to utilise.

PyMark was developed as a response to this. PyMark is (supposedly) easy to setup and is completely open source.

PyMark is coded in Python and is currently only capable of running Python code.

## Overview

### Features

PyMark allows you to create your own programming and informatics problems, similar in format to those at the IOI. PyMark should be easy to set up.

PyMark is not intended to be a platform for running competitions.

### Requirements

PyMark runs in python, and uses mongodb for storing data on it's back end. It requires the python modules `bottle` and `pymongo`, which can be installed by running `pip`.

### Security

PyMark has some *very* limited sandboxing features, which will homefully prevent people doing anything stupid. However, there are well known methods of escaping the sandbox.

## Getting started

### 1. Setting up a database

#### Hosting your own

Feel free to host your own database.

#### Using a service

PyMark has been tested with [mongolab](https://mongolab.com), and it works. Make an account, then create a (free) database, and add the following collections:
- `accounts`
- `code`
- `sessions`
- `submissions`

You'll then need to create a user, then connect PyMark to the database with the URI, which will look something like this: `mongodb://<dbuser>:<dbpassword>@ds031213.mongolab.com:31213/<dbname>`

### 2. Install and run PyMark

Using the command line, navigate to a folder in which you wish to install PyMark, and run `git clone https://github.com/DXsmiley/PyMark.git`. Then naviate to the folder where you wish to store your data files. From there, run `python ../path_to_pymark/server.py`. PyMark will automatically create a number of files and folders. You should then be able to access PyMark on your machine from `localhost:8080`.

If you open the newly created `settings.json` file, you will be able to specify the following parameters.

- "invoke_code": The command line argument used to run python code. Use `{}` to specify the place for the code filename.
- "invoke_shell": Either 0 or 1. Use to specify whether to gain access to the shell environment. Exact results will vary depending on system.
- "db_login": The login URI used for the database.
- "db_name": The name of the database.
- "port": The port on which the server should listen. 8080 by default.

These parameters can also be set through environment variables, which have the same name, but shuld be prefixed by `pymark_`.

### 3. Create a problem

To begin, create a folder in the directory 'problems'. Are create a the following files `settings.json` and `statement.html` within it.

Copy the following data into `settings.json`:

	{
		"grader": "graders.outputonly",
		"name": "problem_name",
		"disabled": false
	}

Currently, only one grader is supported, so don't fiddle with it. `problem_name` is the name of the problem and can be changed to whatever you want. If you want to diable a problem, you can set disabled to true. People will still be able to view the problem, but will be unable to submit. Also, a warning message will be disabled on the problem's page. Finally the property `"required solves"` can be added, specifying the number of problems the user must have completed before being allowed to view this problem.

The file `statement.html` is the problem statement. It is a fully-functional html document, however the `html` and `body` tags will be supplied by the server, so you do not need to add them. Below is an example of a valid problem statement.

	<h1>Example Problem</h1>
	<p>This is a problem. Maybe you can solve it?</p>
	<pre>Some preformatted text</pre>
	<p>The <code>code tag</code> is also usefull.</p>

Finally, you should create the file `cases.json`. This file contains all the test cases that the user's code will be run against. Cases are divided into subtasks. Each case has input and output. A single line of input corresponds with a single `input()` call in the user's python code. The user's code must produce the specified output exactly, otherwise it will fail the test case. 

An example `cases.json` file follows:

	{
		"Subtask 1":
		[
			{
				"input": [
					"1 3 2",
					"8 3 7 2 49 3"
				],
				"output": [
					"2 1",
					"7"
				],
				"show result": true
			}
		]
		"Subtask 2":
		[
			{
				"input": [
					"4 70 4",
					"1 76 34 865 382 12 53"
				],
				"output": [
					"4 8",
					"30"
				]
			}
		]
	}

Note that the `"show result"` flag can be used to show the user what their code produced, the correct output *and* the input.

## Furthur help

You can send me a message via GitHub, or through my email dxsmiley@hotmail.com.

Alternately, you might be able to find what your looking for by poking around in the code, although it's not well commented.
