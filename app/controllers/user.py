from flask import request, render_template, flash, redirect, session, g, jsonify, Blueprint
from app.forms import UserAddForm, UserLoginForm, AccountAddForm, TransactionAddForm
from app.models.User import User
from app.models.Client import Client
from app.models.Account import Account

user = Blueprint('user', __name__)
 
BASE_URL, HEADERS = Client.BASE_URL, Client.HEADERS

@user.before_request
def add_g():
    """add curr user to Flask global variable"""
    if session.get("USERNAME") != None:
        user = User(session["USERNAME"])
        g.user = user.get_from_db()

def add_session(username):
    """ add username to Flask session to signify successful authentication"""
    session["USERNAME"] = username
    add_g()

def remove_session():
    """ remove username to stop authentication"""
    session.clear()

@user.route('/signup', methods=["GET", "POST"])
def signup():
    form = UserAddForm()
    username = form.username.data
    
    if form.validate_on_submit() and not User.is_duplicate_username(username):
        name, email, phone_number, password = form.name.data, form.email.data, form.phone_number.data, form.password.data

        user = User(username)
        success_create = user.create_user_with_api(name, email, phone_number, password)
        success_oauth = user.get_oauth_from_api()
        if not success_oauth:
            user.update_refresh_token_from_api()
            user.get_oauth_from_api()
        add_session(username)
        return redirect(f"/users/{username}")
    elif "USERNAME" in session:
        return redirect(f"/users/{username}")
    else:
        if User.is_duplicate_username(username):
            flash("Username already exists", "danger")
        return render_template("signup.html", form=form)


@user.route('/login', methods=["GET", "POST"])
def login():
    form = UserLoginForm()

    if form.validate_on_submit():
        username, password = form.username.data, form.password.data
        if not User.is_authenticated(username, password):
            flash("Incorrect credentials", "danger")
            return render_template("login.html", form=form)
        else:
            add_session(username)
            flash("Welcome back", "success")
        return redirect(f"/users/{username}")
    elif "USERNAME" in session:
        return redirect(f"/users/{username}")
    else:
        return render_template("login.html", form=form)


@user.route('/logout', methods=["GET"])
def logout():
    remove_session()
    return redirect("/signup")


@user.route('/users/<username>')
def get_user(username):
    if session.get("USERNAME") == username:
        user = User(username)
        user_data = user.get_from_api()
        return render_template("user.html", user=user_data)
    elif session.get("USERNAME") != None:
        return redirect(f'/users/{session["USERNAME"]}')
    else:
        return redirect("/signup")
        

@user.route('/users/<username>/accounts', methods=["GET", "POST"])
def get_accounts(username):
    if session.get("USERNAME") == username:
        form = AccountAddForm()
        user = User(username)
        success_get = user.get_accounts_from_api()

        if not success_get:
            user.update_refresh_token_from_api()
            user.get_oauth_from_api()
            user.get_accounts_from_api()
        if form.validate_on_submit():
            account_type, account_name = form.account_type.data, form.account_name.data
            
            data = Account.format_account_data(account_type,account_name)
            success_create = user.create_account_from_api(data)
            if success_create:
                flash(f"Added {account_name}", "success")
            else: 
                flash(f"Fail to add {account_name}", "danger")
            return redirect(f'/users/{username}/accounts')
        else:
            return render_template("account.html", form=form, accounts=user.accounts)
    elif session.get("USERNAME") != None:
        return redirect(f'/users/{session["USERNAME"]}')
    else:
        return redirect("/signup")

@user.route('/users/<username>/accounts/transactions', methods=["GET", "POST"])
def get_transactions(username):
    """
        loads all transactions and transaction form
        modifies select option field for user accounts
    """
    if session.get("USERNAME") == username:
        user = User(username)
        success_get = user.get_accounts_from_api()

        if not success_get:
            user.update_refresh_token_from_api()
            user.get_oauth_from_api()
            user.get_accounts_from_api()
        user.get_transactions_from_api()

        # workaround for wtform for custom select options
        form = TransactionAddForm()
        form.to_account.choices = [(i, " ".join([a['info']['nickname'], a["type"], a["allowed"], a['info']['balance']['currency'], str(a['info']['balance']['amount'])]))  for i, a in enumerate(user.accounts)]
        form.from_account.choices = form.to_account.choices[:]
        
        if form.validate_on_submit():
            to_account_ind, from_account_ind, amount = form.to_account.data, form.from_account.data, form.amount.data
            # workaround for wtform for custom validator, to ensure different accounts
            is_valid_trans = to_account_ind != from_account_ind
            success_create = False

            if is_valid_trans:
                to_account = user.accounts[to_account_ind]
                data = Account.format_transaction_data(to_account["type"], to_account["_id"], amount)
                success_create = user.create_transaction_from_api(data, from_account_ind)    

            if is_valid_trans and success_create:
                flash(f"Transacted {amount}", "success")
            else: 
                flash(f"Fail to Transact {amount}", "danger")

            return redirect(f'/users/{username}/accounts/transactions')
        else:
            return render_template("transaction.html", form=form, transactions=user.transactions)
    elif session.get("USERNAME") != None:
        return redirect(f'/users/{session["USERNAME"]}')
    else:
        return redirect("/signup")


# @user.route('/users')
# def get_users():
#     url = BASE_URL + "/users"
#     resp = requests.get(
#         url,
#         headers=HEADERS
#     )
#     users = resp.json()["users"]
#     result = ""
#     for user in users:
#         result += f"<li> {user}</li>"
#     result = f"<ul>{result}</ul>"
#     return f"<html><body>{result}</body></html>"


# @user.route('/client')
# def get_loan_reserve():
#     url = BASE_URL + "/client?scope=CLIENT|REPORTS,CLIENT|CONTROLS"
#     resp = requests.get(
#         url,
#         headers=HEADERS,
#     )
#     result = resp.json()
#     return f"<html><body>{result}</body></html>"

# create account node
# internal transfer to nodes
# view transactions



# POST Preview One-Time-Loan
# req loan_user_id
# https://uat-api.synapsefi.com/v3.1/users/loan_user_id/nodes

# POST Apply One-Time-Loan
# req: user_ID
# optional query: same_day: [yes, no]
# https://uat-api.synapsefi.com/v3.1/users/user_ID/nodes
