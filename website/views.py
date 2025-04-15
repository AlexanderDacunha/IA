from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Problems, Classroom, Progress, TestCases, ProblemCategory, User
from . import db

views = Blueprint('views', __name__)

@views.route('/')
@login_required
def home():
    # Store all the problems that are in the database and the current user's progress for the problems in variables
    problems = Problems.query.order_by(Problems.id).all()
    categories = ProblemCategory.query.all()
    

    category_progress = []

    for category in categories:
        percent=0
        categoryProblems = Problems.query.filter_by(category_id=category.id).all()
        #print((categoryProblems))
        total_problems = len(categoryProblems)
        completed_problems = 0
        for problem in categoryProblems:

            progress = Progress.query.filter_by(User_ID=current_user.id, Problem_ID=problem.id).all()
            
            for x in progress:
                if x.completed:
                    completed_problems+=1
        #print(completed_problems)

        if total_problems > 0:
            percent = (completed_problems/total_problems * 100) 

        #print(f"Category: {category.name}, Progress: {percent}%")
        category_progress.append({"name" : category.name, "percent" : percent})

    return render_template("home.html", problems=problems, category_progress=category_progress)

@views.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # Store all the problems that are in the database and the current user's progress for the problems in variables
    problems = Problems.query.order_by(Problems.id).all()
    categories = ProblemCategory.query.all()
    

    category_progress = []

    for category in categories:
        percent=0
        categoryProblems = Problems.query.filter_by(category_id=category.id).all()
        #print((categoryProblems))
        total_problems = len(categoryProblems)
        completed_problems = 0
        for problem in categoryProblems:

            progress = Progress.query.filter_by(User_ID=current_user.id, Problem_ID=problem.id).all()
            
            for x in progress:
                if x.completed:
                    completed_problems+=1
        #print(completed_problems)

        if total_problems > 0:
            percent = (completed_problems/total_problems * 100) 

        #print(f"Category: {category.name}, Progress: {percent}%")
        category_progress.append({"name" : category.name, "percent" : percent})

    if request.method == 'POST' and request.form.get('action') == "joinClass":
        # Get the code that the user provides
        class_code = request.form.get('classCode')

        # Find the class with the matching code
        classroom = Classroom.query.filter_by(code=class_code).first()

        # If a classroom is found with the given class code
        if classroom:
            # Add user to the classroom
            current_user.class_id = classroom.id
            db.session.commit() # Save the user's new classroom
            flash("You have successfully joined the class!", 'success')
        # If there is no classroom found with the given class code
        else:
            flash("Invalid class code.", 'error')

        # Redirect the user to a different page (to prevent form resubmission on page reload)
        return redirect(url_for('views.dashboard'))  
    
    if request.method ==  'POST' and request.form.get('action') == "leaveClass":
        current_user.class_id = None
        flash('Successfully left class', 'success')
        db.session.commit()
        return redirect(url_for("views.dashboard"))
    # Send the variables containing the problems and the user's progress to be displayed
    return render_template('dashboard.html', problems=problems, category_progress=category_progress, user_classroom=Classroom.query.get(current_user.class_id))  

# Creates a page view for the class-dashboard 
# @login_requred makes it so that a user has to be logged in to access this page view
@views.route('/class-dashboard', methods=['GET', 'POST'])
@login_required
# My function for the page will check if your roles are either ADMIN or TEACHER and if they are not, you will be ridirected to the HOME page. 
# If you satisfy the role conditions, you will be sent to the proper page
def class_dashboard():

    classroom = Classroom.query.all()
    students = User.query.all()
    selected_classroom = None

    if current_user.role != "Admin" and current_user.role != "Teacher":
        flash('You do not have access to view this page.', 'error')
        return redirect(url_for('views.home'))

    if request.method == "POST" and request.form.get('action') == 'createProblem':
        problemName = request.form.get("problemName").capitalize()
        function = request.form.get("function")
        problemDescription = request.form.get("problemDescription").capitalize()
        problemDifficulty = request.form.get("problemDifficulty").capitalize()
        category_id = request.form.get("category_id")
        problemCategory = ProblemCategory.query.get(category_id)

        if len(problemName) < 3:
            flash("Problem name must be more than 3 characters", 'error')
            return redirect(url_for("views.class_dashboard"))

        elif len(problemDescription) < 3:
            flash("Problem description must be more than 3 characters", 'error')
            return redirect(url_for("views.class_dashboard"))

        newProblem =  Problems(problemName=problemName, function=function, description=problemDescription, difficulty=problemDifficulty, category=problemCategory)
        #print(newProblem.problemName)
        db.session.add(newProblem)
        db.session.commit()
        flash('Problem Successfully Created', 'success')

        problem = Problems.query.filter_by(problemName=problemName).first()
        newProgress = Progress(User_ID=current_user.id, Problem_ID=problem.id)

        db.session.add(newProgress)
        db.session.commit()
        return redirect(url_for("views.class_dashboard"))
    
    if request.method == "POST" and request.form.get('action') == 'deleteProblem':
        problemID = request.form.get("problemToDelete")

        progress = Progress.query.filter_by(User_ID=current_user.id, Problem_ID=problemID).first()
        if progress:
            db.session.delete(progress)
        else:
            flash('No problem progress exists for that problem ID', 'error')

        test_cases = TestCases.query.filter_by(Problem_ID=problemID).all()
        if test_cases:
            for testCase in test_cases:
                db.session.delete(testCase)
        else:
            flash('No test casees found for that problem ID', 'error')

        problem = Problems.query.filter_by(id=problemID).first()
        if problem:
            db.session.delete(problem)
        else:
            flash('No problem exists with that problem ID', 'error')

        if problem and progress:
            db.session.commit()
            flash('Problem Successfully Deleted', 'success')


        return redirect(url_for("views.class_dashboard"))
    
    if request.method == "POST" and request.form.get("action") == 'createTestCase':
        problemID = request.form.get("problem_id")
        input_data = request.form.get('input_data')
        expected_output = request.form.get('expected_output')

        newTestCase = TestCases(Problem_ID=problemID, input_data=input_data, expected_output=expected_output)

        db.session.add(newTestCase)
        db.session.commit()
        flash('New Test Case Successfully Created', 'success')

        return redirect(url_for('views.class_dashboard'))
    
    if request.method == "POST" and request.form.get("action") == 'populateCategoryDB':
        categories = ["Linked List", "Queue", "Tree", "Stack"]
        if not ProblemCategory.query.get(1):
            for category in categories:
                newCategory = ProblemCategory(name=category, description=f'These are the problems about {category}')
                db.session.add(newCategory)
        flash("Already populated", 'error')
        db.session.commit()
        return redirect(url_for("views.class_dashboard"))
    
    if request.method == 'POST' and request.form.get("action") == 'classroomSelection':
        selection = request.form.get("classroomID")
        selected_classroom = Classroom.query.get(selection)


    return render_template('class_dashboard.html', categories=ProblemCategory.query.all(), problems=Problems.query.all(), classroom=classroom, students=students, selected_classroom=selected_classroom)

@views.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@views.route('/problemsets')
@login_required
def problemsets():
    problems = Problems.query.order_by(Problems.id).all()
    categories = ProblemCategory.query.all()
    return render_template('problemsets.html', problems=problems, categories=categories)

@views.route("/<username>/summary")
@login_required
def summary(username):

    if current_user.role == "Student":
        flash("You do not have access to view this page.", 'error')
        return redirect(url_for('views.home'))

    user = User.query.filter_by(username=username).first()
    problems = Problems.query.order_by(Problems.id).all()
    categories = ProblemCategory.query.all()
    percent=0

    category_progress = []

    for category in categories:
        categoryProblems = Problems.query.filter_by(category_id=category.id).all()
        #print((categoryProblems))
        total_problems = len(categoryProblems)
        completed_problems = 0
        for problem in categoryProblems:

            progress = Progress.query.filter_by(User_ID=user.id, Problem_ID=problem.id).all()
            
            for x in progress:
                if x.completed:
                    completed_problems+=1
        #print(completed_problems)

        if total_problems > 0:
            percent = (completed_problems/total_problems * 100) 

        #print(f"Category: {category.name}, Progress: {percent}%")
        category_progress.append({"name" : category.name, "percent" : percent})

    return render_template("summary.html", category_progress=category_progress, username=username, categories=categories, problems=Problems.query.all(), problemProgress=Progress.query.filter_by(User_ID=user.id).all())