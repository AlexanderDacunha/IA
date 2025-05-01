from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from .models import Problems, Progress, ProblemCategory, TestCases
from . import db
import datetime

problems = Blueprint('problems', __name__) 

@problems.route("/<category_name>")
@login_required
def category_page(category_name):
    # Find the category by name using .ilike to ignore if the name is uppercase or lowercase.
    category = ProblemCategory.query.filter(ProblemCategory.name.ilike(category_name)).first_or_404()

    # Get all problems under this category.
    problems = Problems.query.filter_by(category_id=category.id).all()

    return render_template('category_page.html', category=category, problems=problems)


# Defines a route that dynamically captures an integer 'problem_id' from the URL.
# Allows for access to different problem pages based on the problem's ID using a single route.
@problems.route("/<category_name>/Problem<int:problem_id>", methods=["GET", "POST"])
@login_required # Makes only logged in users able to access this route.
def problem_view(problem_id, category_name):
    # Gets a problem from the Problems database using the specific ID given in the URL returning a 404 error if no problems exist for the given ID.
    problem = Problems.query.get_or_404(problem_id)
    category = ProblemCategory.query.get_or_404(problem.category_id)

    # Retrieves the Progress record of the current problem for the current user
    progress = Progress.query.filter_by(User_ID=current_user.id, Problem_ID=problem.id).first()
    test_cases = TestCases.query.filter_by(Problem_ID = problem.id).all()

    # If no progress record exists for the given problem, create one.
    if not progress:
        progress = Progress(User_ID=current_user.id, Problem_ID=problem.id)
        db.session.add(progress)
        db.session.commit()

    userOutput = request.args.getlist("userOutput")

    return render_template('problemset_base.html', problem=problem, categoryName=category.name, test_cases=test_cases, progress=progress, userOutput=userOutput)


# Route to house the checking of the user's code, breaking up my code.
@problems.route("/<category_name>/Problem<int:problem_id>/solve", methods=["POST"])
@login_required
def solve_problem(problem_id, category_name):
    # Retrieve the necessary information for the specific problem.
    problem = Problems.query.get_or_404(problem_id)
    test_cases = TestCases.query.filter_by(Problem_ID=problem_id).all()
    progress = Progress.query.filter_by(User_ID=current_user.id, Problem_ID=problem.id).first()

    # Store the test cases in lists that separate out the expected outputs and what inputs the function should have.
    testCaseInput = []
    testCaseOutput = []
    userOutput = []
    for test in test_cases:
        testCaseInput.append(test.input_data)
        testCaseOutput.append(test.expected_output)
        
    # Get the user's code from the form removing any leading and trailing whitespace.
    userCode = request.form.get("CodeEditorInput").strip()

    # Set the default to have the user pass the exam and check against it.
    passed = True

    # For every test case for this problem, check the expected output vs the user's output.
    for i in range(len(testCaseInput)):
        # Set a variable to contain all of the code that the user input inserting a line with the problem's function that will be tested.
        runThis = userCode + f'\nreturn_me = {problem.function[ : problem.function.find("(") + 1] + testCaseInput[i] + problem.function[problem.function.find(")")]}'
        loc = {}
        # Executes the user's code, 
        try:
            exec(runThis, loc)
            # If there is something that is returned store the value.
            if len(loc) > 0:
                return_this = loc["return_me"]
            
            # If something has been returned
            if return_this:
                # Compares the user's output and the expected output as ints.
                try:
                    if not int(return_this) == int(testCaseOutput[i]):
                        flash(f'Failed Test {i+1}, Expected Output: {testCaseOutput[i]} You returned: {return_this}', 'error')
                        passed = False

                    # Give feedback if the user's return value equals the expected output for the test case.
                    else:
                        flash(f'Passed Test {i+1}', 'success')

                # If they are not ints, then compare them accordingly. 
                except ValueError:
                    if not return_this == testCaseOutput[i]:
                        flash(f'Failed Test {i+1}, Expected Output: {testCaseOutput[i]} You returned: {return_this}', 'error')
                        passed = False

                    # Give feedback if the user's return value equals the expected output for the test case.
                    else:
                        flash(f'Passed Test {i+1}', 'success')
                userOutput.append(return_this)

            # If nothing is returned by the user's code, give feedback to the user and store the problem's progress.
            else:
                flash(f'Failed Test {i+1}, Expected Output: {testCaseOutput[i]} You returned: {return_this}', 'error')
                passed = False
                userOutput.append(return_this)
        # Capture the error in the user's code, displaying the error for the user to see and storing the problem's progress.
        except Exception as e:
            flash(f'{e}, Expected Output: {testCaseOutput[i]}', 'error')
            userOutput.append("Error")
            passed = False
            
        

    # If the user passed all test cases and test cases exist for this problem, update the problem's progress for the user. 
    if passed and len(testCaseInput) > 0:
        flash(f'You Completed this Problem', 'success')
        progress.completed = True
        db.session.commit()

    # If the user did not pass all test cases, give feedback accordingly.
    else:
        flash("keep working on it", 'error')

    
    print(userOutput)
    return redirect(url_for('problemsets_blueprint.problem_view', problem_id=problem.id, category_name=category_name, userOutput=userOutput))

# Houses all the GIF's that show how the datastructures function and look. 
@problems.route("/Descriptions")
@login_required
def categoryNameGIF():
    filenames = []
    Categories = ProblemCategory.query.all()
    for category in Categories:
        filenames.append(category.name.replace(" ", "") + "GIF.gif")
    return render_template("CategoryDescriptions.html", filenames=filenames)