# Fate App v16 — Full Client/Admin Platform

from flask import Flask, redirect, request
import json
import os
import sys
import threading
import time
import webbrowser
import base64

from io import BytesIO
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

app = Flask(__name__)

from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = (
    "postgresql+psycopg2://postgres.gryoyztwbpinlusjpsnm:FateServieces123@aws-1-us-west-2.pooler.supabase.com:6543/postgres"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class Order(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    client = db.Column(
        db.String(100)
    )

    pokemon = db.Column(
        db.Text
    )

    total = db.Column(
        db.Integer
    )

    paid = db.Column(
        db.Boolean,
        default=False
    )

    completed = db.Column(
        db.Boolean,
        default=False
    )

    start_date = db.Column(
        db.String(20)
    )

    completion_date = db.Column(
        db.String(20)
    )

app.secret_key = "fate_secret_key"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ---------- PATH ----------
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    os.chdir(BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ORDERS_FILE = os.path.join(BASE_DIR, "orders.json")
USERS_FILE = os.path.join(BASE_DIR, "users.json")
REQUESTS_FILE = os.path.join(BASE_DIR, "requests.json")

# ---------- USER ----------
class User(UserMixin):

    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    return User(username)

# ---------- HELPERS ----------
def sprite(name):
    return f"https://img.pokemondb.net/sprites/home/normal/{name.lower().replace(' ','-')}.png"


def is_admin():

    return (
        current_user.is_authenticated
        and current_user.id == "admin"
    )

# ---------- USERS ----------
def load_users():

    if not os.path.exists(USERS_FILE):

        default = {
            "admin": generate_password_hash("fate123")
        }

        with open(USERS_FILE, "w") as f:
            json.dump(default, f, indent=4)

    with open(USERS_FILE, "r") as f:
        return json.load(f)

# ---------- REQUESTS ----------
def load_requests():

    return Request.query.all()

def save_requests():

    pass

# ---------- ORDERS ----------
def load_orders():

    if not os.path.exists(ORDERS_FILE):
        return {"orders": [], "counter": 1}

    with open(ORDERS_FILE, "r") as f:
        data = json.load(f)

    for o in data.get("orders", []):

        o.setdefault("paid", False)
        o.setdefault("completed", False)
        o.setdefault("start_date", datetime.now().strftime("%Y-%m-%d"))
        o.setdefault("completion_date", "")
        o.setdefault("pokemon", [])

        o["total"] = sum(
            p.get("price", 0)
            for p in o["pokemon"]
        )

    return data


def save_orders():

    with open(ORDERS_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Request(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    discord = db.Column(db.String(200))

    ign = db.Column(db.String(200))

    pokemon = db.Column(db.Text)

    notes = db.Column(db.Text)

    status = db.Column(db.String(50))

    date = db.Column(db.String(50))
# ---------- GLOBAL ----------
data = load_orders()

# ---------- UI ----------
def layout(content):

    notif_html = ""

    pending_requests = len(load_requests())

    if pending_requests > 0:

        notif_html = f"""

        <div class='notif'>

            🔔 {pending_requests} Pending Request(s)

        </div>

        """
    sidebar = f"""

    <div class='side'>

        <h2>🎮 Fate</h2>
        
        {notif_html}

    """

    # ---------- USER ----------
    if current_user.is_authenticated:

        sidebar += f"""

        <div class='userbox'>

            👤 {current_user.id}

        </div>

        """

    # ---------- ADMIN ----------
    if is_admin():

        sidebar += """

        <a href='/'>Dashboard</a>

        <a href='/current'>Orders</a>

        <a href='/add'>➕ Add Order</a>

        <a href='/import'>📥 Import Order</a>

        <a href='/requests'>📋 Requests</a>

        <a href='/profits'>📈 Profit Analytics</a>

        <a href='/completion-stats'>⏱ Completion Stats</a>

        """

    # ---------- EVERYONE ----------
    sidebar += """

    <a href='/request-order'>
    📝 Submit Request
    </a>

    """

    # ---------- LOGIN/LOGOUT ----------
    if current_user.is_authenticated:

        sidebar += """

        <a href='/logout'>
        🚪 Logout
        </a>

        """

    else:

        sidebar += """

        <a href='/login'>
        🔐 Admin Login
        </a>

        """

    sidebar += "</div>"

    # ---------- FULL PAGE ----------
    return f"""
   
    <head>

    <meta name="viewport"
        content="width=device-width, initial-scale=1">

    <link rel="apple-touch-icon"
        href="/static/icon.png">

    <meta name="apple-mobile-web-app-capable"
        content="yes">

    <meta name="apple-mobile-web-app-status-bar-style"
        content="black-translucent">

    <meta name="apple-mobile-web-app-title"
        content="Fate Services">

    <title>Fate Services</title>

    </head>

    <style>

    body {{
        background:#0d0d14;
        color:white;
        font-family:Segoe UI;
        display:flex;
        margin:0;
    }}

    .side {{
        width:240px;
        background:#111827;
        min-height:100vh;
        padding:15px;
    }}

    .side a {{
        display:block;
        padding:10px;
        text-decoration:none;
        color:white;
        border-radius:8px;
        margin-bottom:5px;
    }}

    .side a:hover {{
        background:#1f2937;
    }}

    .main {{
        flex:1;
        padding:20px;
    }}

    .card {{
        background:#1a1a2e;
        padding:15px;
        border-radius:12px;
        margin-bottom:15px;
    }}

    .pokemon {{
        background:#141426;
        padding:10px;
        border-radius:10px;
        margin-top:10px;
        display:flex;
        gap:10px;
    }}

    .pokemon img {{
        width:60px;
        height:60px;
    }}

    .btn {{
        padding:8px 12px;
        border:none;
        border-radius:8px;
        background:#00b894;
        color:white;
        text-decoration:none;
        cursor:pointer;
        display:inline-block;
        margin:3px;
    }}

    input,
    select,
    textarea {{
        width:100%;
        padding:10px;
        border:none;
        border-radius:8px;
        margin-top:5px;
        margin-bottom:10px;
    }}

    .stat {{
        background:#141426;
        padding:12px;
        border-radius:10px;
        margin-bottom:10px;
    }}

    .userbox {{
        background:#141426;
        padding:10px;
        border-radius:8px;
        margin-bottom:15px;
    }}

.notif{{

    background:#ff0055;

    color:white;

    padding:10px;

    border-radius:10px;

    margin-top:15px;

    font-weight:bold;

    text-align:center;

    animation:pulse 1.5s infinite;
}}

@keyframes pulse{{

    0%{{opacity:1;}}

    50%{{opacity:.5;}}

    100%{{opacity:1;}}

}}
  
  </style>

    {sidebar}

    <div class='main'>

        {content}

    </div>

    """
# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        users = load_users()

        username = request.form.get('username')
        password = request.form.get('password')

        if (
            username in users
            and check_password_hash(
                users[username],
                password
            )
        ):

            login_user(User(username))

            return redirect('/')

        return layout("<h2>Invalid Login</h2>")

    return layout("""

    <h2>Login</h2>

    <form method='post'>

        Username:
        <input name='username'>

        Password:
        <input type='password' name='password'>

        <button class='btn'>Login</button>

    </form>
    """)

# ---------- REGISTER ----------
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        users = load_users()

        username = request.form.get('username')
        password = request.form.get('password')

        if username in users:
            return layout("<h2>User already exists</h2>")

        users[username] = generate_password_hash(password)

        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)

        return redirect('/login')

    return layout("""

    <h2>Create Account</h2>

    <form method='post'>

        Username:
        <input name='username'>

        Password:
        <input type='password' name='password'>

        <button class='btn'>Create Account</button>

    </form>
    """)

# ---------- LOGOUT ----------
@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect('/login')

# ---------- DASHBOARD ----------
@app.route('/')
@login_required
def home():

    orders = Order.query.all()

    total = sum(
        o.total or 0
        for o in orders
    )

    unpaid = sum(
        o.total or 0
        for o in orders
        if not o.paid
    )

    html = f"""

    <div class='stat'>
        💰 Total Revenue: {total:,}¥
    </div>

    <div class='stat'>
        🔴 Unpaid Revenue: {unpaid:,}¥
    </div>
    """

    return layout(html)

# ---------- CURRENT ----------
@app.route('/current')
@login_required
def current():

    html = "<h2>Orders</h2>"

    sorted_orders = Order.query.order_by(
        Order.completed.asc(),
        Order.paid.asc(),
        Order.id.desc()
    ).all()

    for o in sorted_orders:

        pokemon = json.loads(o.pokemon)

        total = sum(

            p.get("price", 0)

            for p in pokemon

        )

        paid_status = (
            "🟢 Paid"
            if o.paid
            else "🔴 Unpaid"
        )

        complete_status = (
            "✅ Completed"
            if o.completed
            else "🟡 In Progress"
        )

        html += f"""

        <div class='card'
             onclick="toggleOrder('o{o.id}', 'arrow{o.id}')"
             style='cursor:pointer;
                    display:flex;
                    justify-content:space-between;
                    align-items:center;'>

            <div>

                <h3 style='margin:0;'>

                    {o.client}

                </h3>

                <div style='opacity:0.8;'>

                    Order #{o.id}

                </div>

                <div style='margin-top:5px;'>

                    💰 {total:,}¥

                </div>

                <div>

                    {paid_status} |
                    {complete_status}

                </div>

            </div>

            <div id='arrow{o.id}'
                 style='font-size:24px;
                        transition:0.2s;'>

                ▼

            </div>

        </div>

        <div id='o{o.id}'
             style='display:none;'>

            <div class='stat'>

                📅 Started:
                {o.start_date}<br>

                🏁 Completed:
                {o.completion_date or 'In Progress'}

            </div>
        """

        # ---------- POKEMON ----------
        for p in pokemon:

            start = p.get("start", 0)

            end = p.get("end", 0)

            gain = end - start

            level_cost = p.get(
                'level_cost',
                max(0, gain // 10)
            )

            ev_type = p.get(
                'ev_type',
                'None'
            )

            ev_cost = p.get(
                'ev_cost',
                0
            )

            html += f"""

            <div class='pokemon'>

                <img src='{sprite(p['name'])}'>

                <div>

                    <b>{p['name']}</b><br>

                    🧮
                    {start:,}
                    →
                    {end:,}

                    (+{gain:,})<br>

            """

            # ---------- LEVEL COST ----------
            if level_cost > 0:

                html += f"""

                📈 Leveling Cost:
                {level_cost:,}¥<br>

                """

            # ---------- EV COST ----------
            if ev_type != 'None':

                html += f"""

                ⚡ {ev_type}:
                {ev_cost:,}¥<br>

                """

            # ---------- TOTAL ----------
            html += f"""

                    💰
                    {p.get('price',0):,}¥

                </div>

            </div>
            """

        # ---------- ADMIN BUTTONS ----------
        if is_admin():

            html += f"""

            <br>

            <a href='/pay/{o.id}'
               class='btn'>

               💰 Paid

            </a>

            <a href='/complete/{o.id}'
               class='btn'>

               🏁 Complete

            </a>

            <a href='/delete/{o.id}'
               class='btn'>

               🗑 Delete

            </a>
            """

        html += "</div>"

    # ---------- TOGGLE SCRIPT ----------
    html += """

    <script>

    function toggleOrder(id, arrowId){

        let e =
            document.getElementById(id);

        let arrow =
            document.getElementById(arrowId);

        if(
            e.style.display === "none"
            || e.style.display === ""
        ){

            e.style.display = "block";

            arrow.style.transform =
                "rotate(180deg)";

        }
        else{

            e.style.display = "none";

            arrow.style.transform =
                "rotate(0deg)";
        }
    }

    </script>
    """

    return layout(html)

# ---------- ADD ORDER ----------
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():

    if not is_admin():
        return redirect('/')

    if request.method == 'POST':

        client = request.form.get('client')

        pokemon = []

        names = request.form.getlist('pokemon')
        starts = request.form.getlist('start')
        ends = request.form.getlist('end')
        evs = request.form.getlist('evs')

        total = 0

        for i in range(len(names)):

            if not names[i].strip():
                continue

            start = int(starts[i] or 0)
            end = int(ends[i] or 0)

            gain = max(0, end - start)

            price = gain // 10

            ev_type = evs[i]

            if ev_type.strip():
                price += 12000

            total += price

            pokemon.append({

                'name': names[i],

                'start': start,

                'end': end,

                'ev_type': ev_type,

                'price': price
            })

        new_order = Order(

            client=client,

            pokemon=json.dumps(pokemon),

            total=total,

            paid=False,

            completed=False,

            start_date=datetime.now().strftime('%Y-%m-%d'),

            completion_date=''
        )

        db.session.add(new_order)

        db.session.commit()

        return redirect('/current')

    return layout("""

    <h2>➕ Add Order</h2>

    <form method='post'>

        Client Name:
        <input name='client'>

        <div id='pokemonRows'></div>

        <button type='button'
                class='btn'
                onclick='addPokemon()'>

            ➕ Add Pokémon

        </button>

        <br><br>

        <button class='btn'>

            ✅ Create Order

        </button>

    </form>

    <script>

    function addPokemon(){

        let d = document.createElement('div');

        d.className = 'pokemon';

        d.innerHTML = `

        <div style='width:100%'>

        Pokémon:
        <input name='pokemon'>

        Start EXP:
        <input name='start'>

        Target EXP:
        <input name='end'>

        EV Training:
        <input name='evs'
               placeholder='Leave blank for none'>

        <button type='button'
                class='btn'
                onclick='this.parentElement.parentElement.remove()'>

            ❌ Remove

        </button>

        </div>
        `;

        document
            .getElementById('pokemonRows')
            .appendChild(d);
    }

    addPokemon();

    </script>
    """)
# ---------- IMPORT WORK ORDER ----------
@app.route('/import', methods=['GET', 'POST'])
@login_required
def import_order():

    if not is_admin():
        return redirect('/')

    if request.method == 'POST':

        text = request.form.get('text', '')

        lines = text.splitlines()

        pokemon = []

        current = None

        total = 0

        for raw in lines:

            line = raw.strip()

            if not line:
                continue

            # ---------- SKIP ----------
            if (
                'Fate Services' in line
                or 'Overall Progress' in line
                or 'TOTAL:' in line
                or 'Thank you' in line
                or '━━━━━━━━' in line
            ):
                continue

            # ---------- POKEMON NAME ----------
            if (
                '🧮' not in line
                and '💰' not in line
                and 'Leveling Cost' not in line
                and 'EV Training' not in line
                and '⬜' not in line
                and '🟩' not in line
                and '→' not in line
                and len(line) < 30
            ):

                # save previous pokemon
                if current:

                    pokemon.append(current)

                    total += current['price']

                current = {

                    'name': line,

                    'start': 0,

                    'end': 0,

                    'ev_type': 'None',

                    'level_cost': 0,

                    'ev_cost': 0,

                    'price': 0
                }

            # ---------- EXP ----------
            elif '→' in line and current:

                try:

                    parts = line.split('→')

                    start = int(
                        parts[0]
                        .replace(',', '')
                        .strip()
                    )

                    end = int(
                        parts[1]
                        .split('(')[0]
                        .replace(',', '')
                        .strip()
                    )

                    current['start'] = start

                    current['end'] = end

                except:
                    pass

            # ---------- LEVELING COST ----------
            elif (
                'Leveling Cost:' in line
                and current
            ):

                try:

                    lvl_price = int(

                        line.split(':')[1]

                        .replace('¥', '')

                        .replace(',', '')

                        .strip()
                    )

                    current['level_cost'] = lvl_price

                    current['price'] += lvl_price

                except:
                    pass

            # ---------- STANDARD EV ----------
            elif (
                'Standard EV Training:' in line
                and current
            ):

                current['ev_type'] = 'Standard EV'

                try:

                    ev_price = int(

                        line.split(':')[1]

                        .replace('¥', '')

                        .replace(',', '')

                        .strip()
                    )

                    current['ev_cost'] = ev_price

                    current['price'] += ev_price

                except:
                    pass

            # ---------- CUSTOM EV ----------
            elif (
                'Custom EV Training:' in line
                and current
            ):

                current['ev_type'] = 'Custom EV'

                try:

                    ev_price = int(

                        line.split(':')[1]

                        .replace('¥', '')

                        .replace(',', '')

                        .strip()
                    )

                    current['ev_cost'] = ev_price

                    current['price'] += ev_price

                except:
                    pass

        # ---------- SAVE FINAL ----------
        if current:

            pokemon.append(current)

            total += current['price']

        # ---------- CREATE ORDER ----------
        new_order = Order(

            client=request.form.get('client'),

            pokemon=json.dumps(pokemon),

            total=total,

            paid=False,

            completed=False,

            start_date=datetime.now().strftime('%Y-%m-%d'),

            completion_date=''
        )

        db.session.add(new_order)

        db.session.commit()

        return redirect('/current')

    return layout("""

    <h2>
    📥 Import Discord Work Order
    </h2>

    <form method='post'>

        Client Name:

        <input name='client'>

        Paste Discord Work Order:

        <textarea
            name='text'
            rows='25'></textarea>

        <button class='btn'>

            📥 Import Order

        </button>

    </form>

    """)

# ---------- CLIENT REQUEST ----------
@app.route('/request-order', methods=['GET', 'POST'])
def request_order():

    if request.method == 'POST':

        pokemon = []

        names = request.form.getlist("pokemon")
        services = request.form.getlist("service")
        current_exp = request.form.getlist("current_exp")
        target_exp = request.form.getlist("target_exp")
        evs = request.form.getlist("evs")

        for i in range(len(names)):

            if not names[i].strip():
                continue

            pokemon.append({

                "pokemon": names[i],

                "service": services[i],

                "current_exp": current_exp[i],

                "target_exp": target_exp[i],

                "evs": evs[i]
            })

        discord = request.form.get("discord")

        ign = request.form.get("ign")

        notes = request.form.get("notes")

        new_request = Request(

            discord=discord,

            ign=ign,

            pokemon=json.dumps(pokemon),

            notes=notes,

            status="Pending",

            date=datetime.now().strftime("%m/%d/%Y")
        )

        db.session.add(new_request)

        db.session.commit()

        return layout("<h2>✅ Request Submitted</h2>")

    return layout("""

    <h2>Submit Order Request</h2>

    <form method='post'>

        Discord Name:
        <input name='discord'>

        IGN:
        <input name='ign'>

        <div id='pokemonRows'></div>

        <button type='button'
                class='btn'
                onclick='addPokemon()'>

            ➕ Add Pokémon

        </button>

        <br><br>

        Additional Notes:

        <textarea name='notes'></textarea>

        <button class='btn'>
            Submit Request
        </button>

    </form>

    <script>

    function addPokemon(){

        let d = document.createElement('div');

        d.className = 'pokemon';

        d.innerHTML = `

        <div style='width:100%'>

        Pokémon:
        <input name='pokemon'>

        Service:
        <select name='service'>
            <option>Leveling</option>
            <option>EV Training</option>
            <option>Leveling + EV</option>
            <option>Custom</option>
        </select>

        Current EXP:
        <input name='current_exp'>

        Target EXP:
        <input name='target_exp'>

        EV Spread:
        <input name='evs'>

        <button type='button'
                class='btn'
                onclick='this.parentElement.parentElement.remove()'>

            ❌ Remove

        </button>

        </div>
        `;

        document
            .getElementById('pokemonRows')
            .appendChild(d);
    }

    addPokemon();

    </script>
    """)

# ---------- ADMIN REQUESTS ----------
@app.route('/requests')
@login_required
def requests():

    if not is_admin():
        return redirect('/')

    reqs = load_requests()

    html = "<h2>📋 Requests</h2>"

    reqs = sorted(
        reqs,
        key=lambda r: r.id,
        reverse=True
    )

    for r in reqs:

        estimated_total = 0

        pokemon_html = ""

        for p in json.loads(r.pokemon):

            service = p.get("service", "")

            current_exp = int(
                p.get("current_exp") or 0
            )

            target_exp = int(
                p.get("target_exp") or 0
            )

            price = 0

            if (
                "Leveling" in service
                and target_exp > current_exp
            ):

                price += (
                    target_exp - current_exp
                ) // 10

            if "EV" in service:
                price += 12000

            estimated_total += price

            pokemon_html += f"""

            <div class='pokemon'>

                <img src='{sprite(p['pokemon'])}'>

                <div>

                    <b>{p['pokemon']}</b><br>

                    📦 {service}<br>

                    🧮 {current_exp:,}
                    →
                    {target_exp:,}<br>

                    ⚡ {p.get('evs', 'None')}<br>

                    💰 {price:,}¥

                </div>

            </div>
            """

        html += f"""

<div class='card'>

    <h3>{r.discord}</h3>

    👤 IGN: {r.ign}<br>

    📅 {r.date}<br>

    📌 {r.status}

    <br><br>

    {pokemon_html}

    <div class='stat'>

        💰 Estimated Total:
        {estimated_total:,}¥

    </div>

    <div class='stat'>

        📝 {r.notes or None}

    </div>

    <a href='/edit-request/{r.id}'
       class='btn'>

       ✏ Edit

    </a>

    <a href='/approve-request/{r.id}'
       class='btn'>

       ✅ Approve + Convert

    </a>

    <a href='/deny-request/{r.id}'
       class='btn'>

       ❌ Deny

    </a>

</div>
"""

    return layout(html)

# ---------- APPROVE ----------
@app.route('/approve-request/<int:i>')
@login_required
def approve_request(i):

    if not is_admin():
        return redirect('/')

    r = Request.query.get(i)

    if not r:
        return redirect('/requests')

    pokemon = []

    total = 0

    for p in json.loads(r.pokemon):

        service = p.get('service', '')

        current_exp = int(
            p.get('current_exp', 0)
        )

        target_exp = int(
            p.get('target_exp', 0)
        )

        price = 0

        if (
            'Leveling' in service
            and target_exp > current_exp
        ):

            price += (
                target_exp - current_exp
            ) // 10

        if 'EV' in service:

            price += 12000

        total += price

        pokemon.append({

            'name': p.get('pokemon'),

            'price': price,

            'type': 'leveling',

            'start': current_exp,

            'end': target_exp,

            'ev_type': p.get('evs', '')
        })

    new_order = Order(

        client=r.discord,

        pokemon=json.dumps(pokemon),

        total=total,

        paid=False,

        completed=False,

        start_date=datetime.now().strftime('%Y-%m-%d'),

        completion_date=''
    )

    db.session.add(new_order)

    # DELETE REQUEST AFTER APPROVAL
    db.session.delete(r)

    db.session.commit()

    return redirect('/current')

# ---------- DENY ----------
@app.route('/deny-request/<int:i>')
@login_required
def deny_request(i):

    if not is_admin():
        return redirect('/')

    r = Request.query.get(i)

    if r:

        db.session.delete(r)

        db.session.commit()

    return redirect('/requests')

# ---------- EDIT REQUEST ----------
@app.route('/edit-request/<int:i>',
           methods=['GET', 'POST'])
@login_required
def edit_request(i):

    return redirect('/requests')

    # ---------- SAVE ----------
    if request.method == 'POST':

        req['discord'] = request.form.get(
            'discord'
        )

        req['ign'] = request.form.get(
            'ign'
        )

        req['notes'] = request.form.get(
            'notes'
        )

        pokemon = []

        names = request.form.getlist(
            'pokemon'
        )

        services = request.form.getlist(
            'service'
        )

        current_exp = request.form.getlist(
            'current_exp'
        )

        target_exp = request.form.getlist(
            'target_exp'
        )

        evs = request.form.getlist(
            'evs'
        )

        for x in range(len(names)):

            pokemon.append({

                'pokemon': names[x],

                'service': services[x],

                'current_exp':
                    current_exp[x],

                'target_exp':
                    target_exp[x],

                'evs':
                    evs[x]
            })

        req['pokemon'] = pokemon

        save_requests(reqs)

        return redirect('/requests')

    # ---------- FORM ----------
    pokemon_html = ""

    for p in req.get('pokemon', []):

        pokemon_html += f"""

        <div class='pokemon'>

            <div style='width:100%'>

            Pokémon:
            <input name='pokemon'
                   value='{p['pokemon']}'>

            Service:
            <select name='service'>

                <option
                {'selected' if p['service']=='Leveling' else ''}>
                Leveling
                </option>

                <option
                {'selected' if p['service']=='EV Training' else ''}>
                EV Training
                </option>

                <option
                {'selected' if p['service']=='Leveling + EV' else ''}>
                Leveling + EV
                </option>

                <option
                {'selected' if p['service']=='Custom' else ''}>
                Custom
                </option>

            </select>

            Current EXP:
            <input name='current_exp'
                   value='{p['current_exp']}'>

            Target EXP:
            <input name='target_exp'
                   value='{p['target_exp']}'>

            EV Spread:
            <input name='evs'
                   value='{p['evs']}'>

            </div>

        </div>
        """

    return layout(f"""

    <h2>
    ✏ Edit Request
    </h2>

    <form method='post'>

        Discord:
        <input name='discord'
               value='{req['discord']}'>

        IGN:
        <input name='ign'
               value='{req['ign']}'>

        {pokemon_html}

        Notes:

        <textarea name='notes'>
        {req.get('notes','')}
        </textarea>

        <button class='btn'>

            💾 Save Changes

        </button>

    </form>
    """)

# ---------- PAY ----------
@app.route('/pay/<int:i>')
@login_required
def pay(i):

    if not is_admin():
        return redirect('/')

    order = Order.query.get(i)

    if order:

        order.paid = True

        db.session.commit()

    return redirect('/current')

# ---------- COMPLETE ----------
@app.route('/complete/<int:i>')
@login_required
def complete(i):

    if not is_admin():
        return redirect('/')

    order = Order.query.get(i)

    if order:

        order.completed = True

        order.completion_date = (
            datetime.now().strftime('%Y-%m-%d')
        )

        db.session.commit()

    return redirect('/current')

# ---------- DELETE ----------
@app.route('/delete/<int:i>')
@login_required
def delete(i):

    if not is_admin():
        return redirect('/')

    order = Order.query.get(i)

    if order:

        db.session.delete(order)

        db.session.commit()

    return redirect('/current')

# ---------- PROFIT ANALYTICS ----------
@app.route('/profits')
@login_required
def profits():

    if not is_admin():
        return redirect('/')

    completed_orders = [

        o for o in Order.query.all()

        if (
            o.completed
            and o.completion_date
        )
    ]

    if not completed_orders:

        return layout(
            "<h2>No completed orders yet.</h2>"
        )

    # ---------- SORT ----------
    completed_orders = sorted(

        completed_orders,

        key=lambda o:
            datetime.strptime(
                o.completion_date,
                '%Y-%m-%d'
            )
    )

    # ---------- DATA ----------
    dates = []
    totals = []

    daily_profit = {}
    monthly_profit = {}

    cumulative = []

    running_total = 0

    for o in completed_orders:

        total = o.total or 0

        raw_date = o.completion_date

        dt = datetime.strptime(
            raw_date,
            '%Y-%m-%d'
        )

        formatted_date = dt.strftime(
            '%m/%d/%Y'
        )

        running_total += total

        dates.append(formatted_date)

        totals.append(total)

        cumulative.append(running_total)

        # daily
        daily_profit[formatted_date] = (

            daily_profit.get(
                formatted_date,
                0
            )

            + total
        )

        # monthly
        month = dt.strftime('%m/%Y')

        monthly_profit[month] = (

            monthly_profit.get(
                month,
                0
            )

            + total
        )

    # ==================================================
    # GRAPH 1
    # ==================================================

    plt.figure(figsize=(12,5))

    plt.plot(
        dates,
        cumulative,
        marker='o',
        linewidth=3
    )

    plt.title(
        'Total Profit Over Time'
    )

    plt.xlabel('Date')

    plt.ylabel('Revenue (¥)')

    plt.xticks(rotation=45)

    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    img1 = BytesIO()

    plt.savefig(
        img1,
        format='png',
        bbox_inches='tight'
    )

    plt.close()

    img1.seek(0)

    graph1 = (
        base64.b64encode(
            img1.getvalue()
        ).decode()
    )

    # ==================================================
    # GRAPH 2
    # ==================================================

    months = list(
        monthly_profit.keys()
    )

    month_values = list(
        monthly_profit.values()
    )

    plt.figure(figsize=(12,5))

    plt.bar(
        months,
        month_values
    )

    plt.title(
        'Monthly Order Profits'
    )

    plt.xlabel('Month')

    plt.ylabel('Profit (¥)')

    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    img2 = BytesIO()

    plt.savefig(
        img2,
        format='png',
        bbox_inches='tight'
    )

    plt.close()

    img2.seek(0)

    graph2 = (
        base64.b64encode(
            img2.getvalue()
        ).decode()
    )

    # ==================================================
    # GRAPH 3
    # ==================================================

    days = list(
        daily_profit.keys()
    )

    day_values = list(
        daily_profit.values()
    )

    plt.figure(figsize=(12,5))

    plt.bar(
        days,
        day_values
    )

    plt.title(
        'Daily Profits'
    )

    plt.xlabel('Date')

    plt.ylabel('Profit (¥)')

    plt.xticks(rotation=45)

    plt.grid(True, alpha=0.3)

    plt.tight_layout()

    img3 = BytesIO()

    plt.savefig(
        img3,
        format='png',
        bbox_inches='tight'
    )

    plt.close()

    img3.seek(0)

    graph3 = (
        base64.b64encode(
            img3.getvalue()
        ).decode()
    )

    # ---------- STATS ----------
    total_profit = sum(totals)

    average_order = int(
        total_profit / len(totals)
    )

    highest_order = max(totals)

    # ---------- PAGE ----------
    html = f"""

    <h2>📈 Profit Analytics</h2>

    <div class='stat'>
        💰 Total Profit:
        {total_profit:,}¥
    </div>

    <div class='stat'>
        📦 Completed Orders:
        {len(totals)}
    </div>

    <div class='stat'>
        📊 Average Order:
        {average_order:,}¥
    </div>

    <div class='stat'>
        🏆 Highest Order:
        {highest_order:,}¥
    </div>

    <br>

    <h3>
    📈 Total Profit Over Time
    </h3>

    <img src='data:image/png;base64,{graph1}'
         width='100%'>

    <br><br>

    <h3>
    📅 Monthly Order Profits
    </h3>

    <img src='data:image/png;base64,{graph2}'
         width='100%'>

    <br><br>

    <h3>
    📆 Daily Profits
    </h3>

    <img src='data:image/png;base64,{graph3}'
         width='100%'>

    """

    return layout(html)

# ---------- COMPLETION GRAPH ----------
@app.route('/completion-stats')
@login_required

def completion_stats():

    if not is_admin():
        return redirect('/')

    pokemon_counts = []
    completion_days = []

    for o in Order.query.all():

        if (
            o.completed
            and o.completion_date
        ):

            start = datetime.strptime(
                o.start_date,
                '%Y-%m-%d'
            )

            end = datetime.strptime(
                o.completion_date,
                '%Y-%m-%d'
            )

            days = (end - start).days

            pokemon_counts.append(
                len(json.loads(o.pokemon))
            )

            completion_days.append(days)

    if not pokemon_counts:
        return layout('<h2>No completion stats yet.</h2>')

    plt.figure(figsize=(10,5))

    plt.scatter(
        pokemon_counts,
        completion_days
    )

    plt.xlabel('Pokémon Count')

    plt.ylabel('Completion Days')

    plt.title('Completion Analytics')

    plt.grid(True, alpha=0.3)

    img = BytesIO()

    plt.savefig(
        img,
        format='png',
        bbox_inches='tight'
    )

    plt.close()

    img.seek(0)

    graph_url = (
        base64.b64encode(img.getvalue())
        .decode()
    )

    html = f"""

    <h2>⏱ Completion Analytics</h2>

    <img src='data:image/png;base64,{graph_url}' width='100%'>
    """

    return layout(html)

# ---------- MIGRATE OLD JSON ----------
def migrate_old_orders():

    if not os.path.exists("orders.json"):
        return

    with open("orders.json", "r") as f:

        old_data = json.load(f)

    existing = Order.query.count()

    # avoid duplicate importing
    if existing > 0:
        return

    for o in old_data.get("orders", []):

        new_order = Order(

            client=o.get("client", ""),

            pokemon=json.dumps(
                o.get("pokemon", [])
            ),

            total=o.get("total", 0),

            paid=o.get("paid", False),

            completed=o.get(
                "completed",
                False
            ),

            start_date=o.get(
                "start_date",
                ""
            ),

            completion_date=o.get(
                "completion_date",
                ""
            )
        )

        db.session.add(new_order)

    db.session.commit()

    print("Old orders imported.")

with app.app_context():

    db.create_all()

    migrate_old_orders()

# ---------- RUN ----------
if __name__ == "__main__":

    if os.environ.get("RENDER") is None:

        def open_browser():

            time.sleep(1)

            webbrowser.open(
                "http://127.0.0.1:5000"
            )

        threading.Thread(
            target=open_browser
        ).start()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )