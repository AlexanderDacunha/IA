import requests
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Problems, Progress, ProblemCategory, TestCases
from . import db
import datetime

problems = Blueprint('problems', __name__) 

@problems.route("/<category_name>")
@login_required
def category_page(category_name):
    # Find the category by name, using .ilike to ignore if the name is uppercase or lowercase.
    category = ProblemCategory.query.filter(ProblemCategory.name.ilike(category_name)).first_or_404()

    # Get all problems under this category.
    problems = Problems.query.filter_by(category_id=category.id).all()

    return render_template('category_page.html', category=category, problems=problems)


# Defines a route that dynamically captures an integer 'problem_id' from the URL.
# Allows for access to different problem pages based on the problem's ID using a single route.
@problems.route("/<category_name>/Problem<int:problem_id>", methods=["GET", "POST"])
@login_required # Makes only logged in users able to access this route.
def problem_view(problem_id, category_name):
    # Gets a problem from the Problems database using the specific ID given in the URL.
    # If no problem with the ID exists, it returns a 404 error.
    problem = Problems.query.get_or_404(problem_id)
    category = ProblemCategory.query.get_or_404(problem.category_id)

    # Retrieves the Progress record of the current problem for the current user
    progress = Progress.query.filter_by(User_ID=current_user.id, Problem_ID=problem.id).first()
    test_cases = TestCases.query.filter_by(Problem_ID = problem.id).all()

    if not progress:
        progress = Progress(User_ID=current_user.id, Problem_ID=problem.id)
        db.session.add(progress)
        db.session.commit()
    
    #if request.method == "POST":
        # Gets the code that the user submitted in the text box.
        #code = request.form.get("CodeEditorInput").strip()

        #print(request.form.get("CodeEditorInput").strip())

        # If the user has submitted anything, mark the problem as completed.
        #if code and not progress.completed:
            #progress.completed = True # Updates the completion status of the problem.
            #db.session.commit() # Saves the update to the completion status.

            # Redirects the user back to the problem upon submission, making it so that reloading the page does not submit the form.
            # Dynamic routing ensures that the correct problem is shown by passing through the 'problem_id' parameter.
            #return redirect(url_for('problemsets_blueprint.problem_view', problem_id=problem.id, category_name=category.name))
        
        
        

    # Renders the template for the problem page, dynamically passing through the problem's details.
    return render_template('problemset_base.html', problem=problem, categoryName=category.name, test_cases=test_cases, progress=progress)



@problems.route("/<category_name>/Problem<int:problem_id>/solve", methods=["POST"])
@login_required
def solve_problem(problem_id, category_name):
    problem = Problems.query.get_or_404(problem_id)
    test_cases = TestCases.query.filter_by(Problem_ID=problem_id).all()
    progress = Progress.query.filter_by(User_ID=current_user.id, Problem_ID=problem.id).first()

    testCaseInput = []
    testCaseOutput = []
    for test in test_cases:
        testCaseInput.append(test.input_data)
        testCaseOutput.append(test.expected_output)

    userCode = request.form.get("CodeEditorInput").strip()

    passed = True
    print(datetime.datetime.now())

    for i in range(len(testCaseInput)):
        runThis = userCode + f'\nreturn_me = {problem.function[ : problem.function.find("(") + 1] + testCaseInput[i] + problem.function[problem.function.find(")")]}'
        loc = {}
        try:
            exec(runThis, loc)
            if len(loc) > 0:
                return_this = loc["return_me"]
            
            if return_this:
                if not (int(return_this) == int(testCaseOutput[i])):
                    flash(f'Failed Test {i+1}, Expected Output: {testCaseOutput[i]} You returned: {return_this}', 'error')
                    passed = False
                else:
                    flash(f'Passed Test {i+1}', 'success')
            else:
                flash(f'Failed Test {i+1}, Expected Output: {testCaseOutput[i]} You returned: {return_this}', 'error')
                passed = False
        except Exception as e:
            flash(f'{e}...What did you even write, Expected Output: {testCaseOutput[i]}', 'error')
            passed = False


    if passed and len(testCaseInput) > 0:
        flash(f'You Completed this Problem', 'success')
        progress.completed = True
        db.session.commit()

    else:
        flash("keep working on it", 'error')

    #print(userCode)

    return redirect(url_for('problemsets_blueprint.problem_view', problem_id=problem.id, category_name=category_name))
    #return render_template("solving.html", problem_id=problem.id, category_name=category_name, test_cases=test_cases, userCode=userCode)

@problems.route("/<categoryName>GIF")
@login_required
def categoryNameGIF(categoryName):
    categoryName = "Linked List"
    filename = categoryName.replace(" ", "") + "GIF.gif"
    return render_template("LinkedListDesc.html", categoryName=categoryName, filename=filename)