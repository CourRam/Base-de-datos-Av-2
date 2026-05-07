from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
app.secret_key = "bda_proyecto"


MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["empresa_db"]


employees_col    = db["employee"]
departments_col  = db["department"]
dept_loc_col     = db["dept_locations"]
projects_col     = db["project"]
works_on_col     = db["works_on"]
dependents_col   = db["dependent"]



@app.route("/")
def index():
    stats = {
        "employees":   employees_col.count_documents({}),
        "departments": departments_col.count_documents({}),
        "projects":    projects_col.count_documents({}),
        "works_on":    works_on_col.count_documents({}),
        "dependents":  dependents_col.count_documents({}),
    }
    
    pepeline = [{"$group":{"_id":None,"avg":{"$avg":"$Salary"},"max":{"$max":"$Salary"},"min":{"$min":"$Salary"}}}]
    sal = list(employees_col.aggregate(pepeline))
    if sal:
        stats["avg_salary"] = round(sal[0]["avg"], 2)
        stats["max_salary"] = sal[0]["max"]
        stats["min_salary"] = sal[0]["min"]
    return render_template("index.html", stats=stats)



@app.route("/employees")
def employees():
    search = request.args.get("q", "")
    dept_filter = request.args.get("dno", "")
    query = {}
    if search:
        query["$or"] = [
            {"Fname":{"$regex":search,"$options":"i"}},
            {"Lname":{"$regex":search,"$options":"i"}},
            {"Ssn":  {"$regex":search,"$options":"i"}},
        ]
    if dept_filter:
        query["Dno"] = int(dept_filter)
    emps = list(employees_col.find(query))
    depts = list(departments_col.find())
    return render_template("employees.html", employees=emps, departments=depts,
                           search=search, dept_filter=dept_filter)


@app.route("/employees/new", methods=["GET","POST"])
def employee_new():
    depts = list(departments_col.find())
    if request.method == "POST":
        doc = {
            "Fname":     request.form["Fname"],
            "Minit":     request.form["Minit"],
            "Lname":     request.form["Lname"],
            "Ssn":       request.form["Ssn"],
            "Bdate":     request.form["Bdate"],
            "Address":   request.form["Address"],
            "Sex":       request.form["Sex"],
            "Salary":    float(request.form["Salary"]),
            "Super_ssn": request.form.get("Super_ssn") or None,
            "Dno":       int(request.form["Dno"]),
        }
        if employees_col.find_one({"Ssn": doc["Ssn"]}):
            flash("SSN ya existe.", "danger")
        else:
            employees_col.insert_one(doc)
            flash("Empleado agregado.", "success")
            return redirect(url_for("employees"))
    return render_template("employee_form.html", emp=None, departments=depts, action="Nuevo")

@app.route("/employees/edit/<id>", methods=["GET","POST"])
def employee_edit(id):
    emp = employees_col.find_one({"_id": ObjectId(id)})
    depts = list(departments_col.find())
    if request.method == "POST":
        employees_col.update_one({"_id": ObjectId(id)}, {"$set":{
            "Fname":     request.form["Fname"],
            "Minit":     request.form["Minit"],
            "Lname":     request.form["Lname"],
            "Bdate":     request.form["Bdate"],
            "Address":   request.form["Address"],
            "Sex":       request.form["Sex"],
            "Salary":    float(request.form["Salary"]),
            "Super_ssn": request.form.get("Super_ssn") or None,
            "Dno":       int(request.form["Dno"]),
        }})
        flash("Empleado actualizado.", "success")
        return redirect(url_for("employees"))
    return render_template("employee_form.html", emp=emp, departments=depts, action="Editar")

@app.route("/employees/delete/<id>")
def employee_delete(id):
    employees_col.delete_one({"_id": ObjectId(id)})
    flash("Empleado eliminado.", "warning")
    return redirect(url_for("employees"))


@app.route("/departments")
def departments():
    depts = list(departments_col.find())
    for d in depts:
        d["locations"] = [l["Dlocation"] for l in dept_loc_col.find({"Dnumber": d["Dnumber"]})]
        mgr = employees_col.find_one({"Ssn": d["Mgr_ssn"]})
        d["manager_name"] = f"{mgr['Fname']} {mgr['Lname']}" if mgr else "—"
        d["emp_count"] = employees_col.count_documents({"Dno": d["Dnumber"]})
    return render_template("departments.html", departments=depts)

@app.route("/departments/new", methods=["GET","POST"])
def department_new():
    emps = list(employees_col.find())
    if request.method == "POST":
        doc = {
            "Dname":          request.form["Dname"],
            "Dnumber":        int(request.form["Dnumber"]),
            "Mgr_ssn":        request.form["Mgr_ssn"],
            "Mgr_start_date": request.form["Mgr_start_date"],
        }
        departments_col.insert_one(doc)
        locations = [l.strip() for l in request.form.get("locations","").split(",") if l.strip()]
        for loc in locations:
            dept_loc_col.insert_one({"Dnumber": doc["Dnumber"], "Dlocation": loc})
        flash("Departamento agregado.", "success")
        return redirect(url_for("departments"))
    return render_template("department_form.html", dept=None, employees=emps, action="Nuevo")

@app.route("/departments/edit/<id>", methods=["GET","POST"])
def department_edit(id):
    dept = departments_col.find_one({"_id": ObjectId(id)})
    emps = list(employees_col.find())
    locs = [l["Dlocation"] for l in dept_loc_col.find({"Dnumber": dept["Dnumber"]})]
    if request.method == "POST":
        departments_col.update_one({"_id": ObjectId(id)}, {"$set":{
            "Dname":          request.form["Dname"],
            "Mgr_ssn":        request.form["Mgr_ssn"],
            "Mgr_start_date": request.form["Mgr_start_date"],
        }})
        dept_loc_col.delete_many({"Dnumber": dept["Dnumber"]})
        locations = [l.strip() for l in request.form.get("locations","").split(",") if l.strip()]
        for loc in locations:
            dept_loc_col.insert_one({"Dnumber": dept["Dnumber"], "Dlocation": loc})
        flash("Departamento actualizado.", "success")
        return redirect(url_for("departments"))
    dept["current_locations"] = ", ".join(locs)
    return render_template("department_form.html", dept=dept, employees=emps, action="Editar")

@app.route("/departments/delete/<id>")
def department_delete(id):
    dept = departments_col.find_one({"_id": ObjectId(id)})
    dept_loc_col.delete_many({"Dnumber": dept["Dnumber"]})
    departments_col.delete_one({"_id": ObjectId(id)})
    flash("Departamento eliminado.", "warning")
    return redirect(url_for("departments"))


@app.route("/projects")
def projects():
    projs = list(projects_col.find())
    for p in projs:
        dept = departments_col.find_one({"Dnumber": p["Dnum"]})
        p["dept_name"] = dept["Dname"] if dept else "—"
        p["worker_count"] = works_on_col.count_documents({"Pno": p["Pnumber"]})
    return render_template("projects.html", projects=projs)

@app.route("/projects/new", methods=["GET","POST"])
def project_new():
    depts = list(departments_col.find())
    if request.method == "POST":
        doc = {
            "Pname":     request.form["Pname"],
            "Pnumber":   int(request.form["Pnumber"]),
            "Plocation": request.form["Plocation"],
            "Dnum":      int(request.form["Dnum"]),
        }
        projects_col.insert_one(doc)
        flash("Proyecto agregado.", "success")
        return redirect(url_for("projects"))
    return render_template("project_form.html", proj=None, departments=depts, action="Nuevo")

@app.route("/projects/edit/<id>", methods=["GET","POST"])
def project_edit(id):
    proj = projects_col.find_one({"_id": ObjectId(id)})
    depts = list(departments_col.find())
    if request.method == "POST":
        projects_col.update_one({"_id": ObjectId(id)}, {"$set":{
            "Pname":     request.form["Pname"],
            "Plocation": request.form["Plocation"],
            "Dnum":      int(request.form["Dnum"]),
        }})
        flash("Proyecto actualizado.", "success")
        return redirect(url_for("projects"))
    return render_template("project_form.html", proj=proj, departments=depts, action="Editar")

@app.route("/projects/delete/<id>")
def project_delete(id):
    projects_col.delete_one({"_id": ObjectId(id)})
    flash("Proyecto eliminado.", "warning")
    return redirect(url_for("projects"))


@app.route("/works_on")
def works_on():
    records = list(works_on_col.find())
    for r in records:
        emp = employees_col.find_one({"Ssn": r["Essn"]})
        r["emp_name"] = f"{emp['Fname']} {emp['Lname']}" if emp else r["Essn"]
        proj = projects_col.find_one({"Pnumber": r["Pno"]})
        r["proj_name"] = proj["Pname"] if proj else str(r["Pno"])
    return render_template("works_on.html", records=records)

@app.route("/works_on/new", methods=["GET","POST"])
def works_on_new():
    emps = list(employees_col.find())
    projs = list(projects_col.find())
    if request.method == "POST":
        hours_raw = request.form.get("Hours","").strip()
        doc = {
            "Essn":  request.form["Essn"],
            "Pno":   int(request.form["Pno"]),
            "Hours": float(hours_raw) if hours_raw else None,
        }
        works_on_col.insert_one(doc)
        flash("Asignación agregada.", "success")
        return redirect(url_for("works_on"))
    return render_template("works_on_form.html", rec=None, employees=emps, projects=projs, action="Nueva")

@app.route("/works_on/edit/<id>", methods=["GET","POST"])
def works_on_edit(id):
    rec = works_on_col.find_one({"_id": ObjectId(id)})
    emps = list(employees_col.find())
    projs = list(projects_col.find())
    if request.method == "POST":
        hours_raw = request.form.get("Hours","").strip()
        works_on_col.update_one({"_id": ObjectId(id)}, {"$set":{
            "Hours": float(hours_raw) if hours_raw else None,
        }})
        flash("Horas actualizadas.", "success")
        return redirect(url_for("works_on"))
    return render_template("works_on_form.html", rec=rec, employees=emps, projects=projs, action="Editar")

@app.route("/works_on/delete/<id>")
def works_on_delete(id):
    works_on_col.delete_one({"_id": ObjectId(id)})
    flash("Asignación eliminada.", "warning")
    return redirect(url_for("works_on"))



@app.route("/dependents")
def dependents():
    deps = list(dependents_col.find())
    for d in deps:
        emp = employees_col.find_one({"Ssn": d["Essn"]})
        d["emp_name"] = f"{emp['Fname']} {emp['Lname']}" if emp else d["Essn"]
    return render_template("dependents.html", dependents=deps)

@app.route("/dependents/new", methods=["GET","POST"])
def dependent_new():
    emps = list(employees_col.find())
    if request.method == "POST":
        doc = {
            "Essn":           request.form["Essn"],
            "Dependent_name": request.form["Dependent_name"],
            "Sex":            request.form["Sex"],
            "Bdate":          request.form["Bdate"],
            "Relationship":   request.form["Relationship"],
        }
        dependents_col.insert_one(doc)
        flash("Dependiente agregado.", "success")
        return redirect(url_for("dependents"))
    return render_template("dependent_form.html", dep=None, employees=emps, action="Nuevo")

@app.route("/dependents/edit/<id>", methods=["GET","POST"])
def dependent_edit(id):
    dep = dependents_col.find_one({"_id": ObjectId(id)})
    emps = list(employees_col.find())
    if request.method == "POST":
        dependents_col.update_one({"_id": ObjectId(id)}, {"$set":{
            "Dependent_name": request.form["Dependent_name"],
            "Sex":            request.form["Sex"],
            "Bdate":          request.form["Bdate"],
            "Relationship":   request.form["Relationship"],
        }})
        flash("Dependiente actualizado.", "success")
        return redirect(url_for("dependents"))
    return render_template("dependent_form.html", dep=dep, employees=emps, action="Editar")

@app.route("/dependents/delete/<id>")
def dependent_delete(id):
    dependents_col.delete_one({"_id": ObjectId(id)})
    flash("Dependiente eliminado.", "warning")
    return redirect(url_for("dependents"))




if __name__ == "__main__":
    app.run(debug=True, port=5000)
