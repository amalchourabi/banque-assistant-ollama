from flask import Flask, request, render_template_string, session, redirect, url_for
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

import sqlite3
import requests
import base64
import os
import uuid


# ============================================================
# APPLICATION
# ============================================================

app = Flask(__name__)

app.secret_key = "change-cette-cle-secrete-en-production"

DB_FILE = "banque.db"

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ============================================================
# CONFIGURATION OLLAMA - PERFORMANCE LOCALE
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_KEEP_ALIVE = "1h"
OLLAMA_NUM_CTX = 4096
OLLAMA_NUM_PREDICT = 180



# ============================================================
# BASE DE DONNEES
# ============================================================

def get_db():

    conn = sqlite3.connect(DB_FILE)

    conn.row_factory = sqlite3.Row

    return conn


# ============================================================
# STYLE LOGIN + DASHBOARD
# ============================================================

STYLE = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=DM+Sans:wght@400;500;600;700&display=swap');


* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: 'DM Sans', Arial, sans-serif;
}


html,
body {
    min-height: 100%;
}


body {
    background: #F6F2E9;
    color: #16262B;
}


/* ============================================================
   LOGIN
   ============================================================ */

.login-wrap {

    min-height: 100vh;

    display: flex;

    align-items: center;

    justify-content: center;

    padding: 20px;

    background:
        radial-gradient(
            circle at top right,
            rgba(201,148,46,0.25),
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #16262B,
            #203A43
        );

}


.card {

    background: #FDFBF7;

    border-radius: 22px;

    box-shadow:
        0 25px 70px
        rgba(0,0,0,0.25);

    padding: 42px;

    width: 100%;

    max-width: 460px;

    border:
        1px solid
        rgba(255,255,255,0.15);

}


.login-brand {

    text-align: center;

    margin-bottom: 28px;

}


.login-logo {

    font-family:
        'Fraunces',
        serif;

    font-size: 30px;

    font-weight: 600;

    color: #16262B;

}


.login-logo span {

    color: #C9942E;

}


.login-subtitle {

    color: #6C7778;

    font-size: 14px;

    margin-top: 8px;

}


h2 {

    color: #16262B;

    margin-bottom: 20px;

}


label {

    display: block;

    margin-bottom: 7px;

    color: #46565B;

    font-size: 14px;

    font-weight: 500;

}


input[type=text],
input[type=password] {

    width: 100%;

    padding: 14px;

    border:
        1px solid
        #DED8CB;

    border-radius: 10px;

    margin-bottom: 18px;

    font-size: 15px;

    background: #FFFFFF;

    outline: none;

    transition: 0.2s;

}


input[type=text]:focus,
input[type=password]:focus {

    border-color: #C9942E;

    box-shadow:
        0 0 0 3px
        rgba(201,148,46,0.12);

}


input[type=submit] {

    width: 100%;

    background: #16262B;

    color: #F6F2E9;

    border: none;

    padding: 14px;

    border-radius: 10px;

    cursor: pointer;

    font-size: 15px;

    font-weight: 600;

    transition: 0.2s;

}


input[type=submit]:hover {

    background: #C9942E;

    color: #16262B;

    transform: translateY(-1px);

}


.erreur {

    color: #A63D35;

    background: #FCE9E7;

    padding: 12px;

    border-radius: 10px;

    margin-top: 15px;

    font-size: 14px;

}


/* ============================================================
   DASHBOARD LAYOUT
   ============================================================ */

.layout {

    display: flex;

    min-height: 100vh;

    background: #F6F2E9;

}


/* ============================================================
   SIDEBAR
   ============================================================ */

.sidebar {

    position: fixed;

    top: 0;

    left: 0;

    width: 280px;

    height: 100vh;

    background: #16262B;

    color: #F6F2E9;

    padding: 28px 20px;

    display: flex;

    flex-direction: column;

    border-right:
        1px solid
        rgba(255,255,255,0.05);

}


.brand-box {

    padding:
        8px
        8px
        30px
        8px;

}


.brand-logo {

    font-family:
        'Fraunces',
        serif;

    font-size: 26px;

    font-weight: 600;

    color: #F6F2E9;

    text-decoration: none;

}


.brand-logo span {

    color: #C9942E;

}


.brand-line {

    width: 45px;

    height: 3px;

    background: #C9942E;

    border-radius: 10px;

    margin-top: 12px;

}


/* ============================================================
   USER BOX
   ============================================================ */

.user-box {

    background:
        rgba(255,255,255,0.07);

    border:
        1px solid
        rgba(255,255,255,0.08);

    border-radius: 16px;

    padding: 16px;

    margin-bottom: 28px;

}


.user-avatar {

    width: 42px;

    height: 42px;

    background: #C9942E;

    color: #16262B;

    border-radius: 50%;

    display: flex;

    align-items: center;

    justify-content: center;

    font-weight: 700;

    font-size: 17px;

    margin-bottom: 10px;

}


.user-name {

    font-size: 15px;

    font-weight: 600;

    color: #FFFFFF;

}


.user-role {

    font-size: 12px;

    color: #B7C4CB;

    margin-top: 4px;

}


/* ============================================================
   NAVIGATION
   ============================================================ */

.sidebar nav {

    flex: 1;

}


.nav-title {

    color: #839497;

    font-size: 11px;

    font-weight: 700;

    letter-spacing: 1px;

    margin:
        0
        10px
        10px;

}


.sidebar .nav-item {

    display: flex;

    align-items: center;

    gap: 12px;

    color: #C8D1D3;

    text-decoration: none;

    padding: 13px 14px;

    border-radius: 11px;

    margin-bottom: 7px;

    font-size: 14px;

    font-weight: 500;

    transition: 0.2s;

}


.sidebar .nav-item:hover {

    background:
        rgba(255,255,255,0.07);

    color: #FFFFFF;

}


.sidebar .nav-item.actif {

    background: #F6F2E9;

    color: #16262B;

    font-weight: 600;

}


.nav-icon {

    font-size: 18px;

}


/* ============================================================
   SIDEBAR BOTTOM
   ============================================================ */

.sidebar-bottom {

    padding-top: 15px;

}


.contact-mini {

    padding: 14px;

    border-radius: 13px;

    background:
        rgba(201,148,46,0.10);

    border:
        1px solid
        rgba(201,148,46,0.15);

    margin-bottom: 14px;

}


.contact-mini-title {

    color: #C9942E;

    font-size: 12px;

    font-weight: 700;

    margin-bottom: 7px;

}


.contact-mini-text {

    color: #B7C4CB;

    font-size: 11px;

    line-height: 1.8;

}


.sidebar .logout-link {

    display: block;

    text-align: center;

    color: #F6F2E9;

    background:
        rgba(255,255,255,0.08);

    text-decoration: none;

    padding: 13px 12px;

    border-radius: 11px;

    font-size: 14px;

    font-weight: 600;

    transition: 0.2s;

}


.sidebar .logout-link:hover {

    background: #D9534F;

}


/* ============================================================
   MAIN
   ============================================================ */

.main {

    margin-left: 280px;

    width:
        calc(100% - 280px);

    padding:
        35px
        50px
        50px;

    max-width: 1500px;

}


/* ============================================================
   HEADER
   ============================================================ */

.dashboard-header {

    display: flex;

    align-items: flex-start;

    justify-content: space-between;

    margin-bottom: 32px;

}


.dashboard-eyebrow {

    color: #C9942E;

    font-size: 12px;

    font-weight: 700;

    text-transform: uppercase;

    letter-spacing: 1.2px;

    margin-bottom: 8px;

}


.dashboard-title {

    font-family:
        'Fraunces',
        serif;

    color: #16262B;

    font-size: 34px;

    font-weight: 500;

    margin: 0;

}


.dashboard-date {

    color: #6C7778;

    font-size: 14px;

    margin-top: 8px;

}


.header-badge {

    background: #FFFFFF;

    border:
        1px solid
        #E5DFD4;

    border-radius: 14px;

    padding: 13px 17px;

    display: flex;

    align-items: center;

    gap: 10px;

    color: #46565B;

    font-size: 13px;

}


.status-dot {

    width: 9px;

    height: 9px;

    background: #5B9A72;

    border-radius: 50%;

    box-shadow:
        0 0 0 4px
        rgba(91,154,114,0.12);

}


/* ============================================================
   STATISTIQUES
   ============================================================ */

.stats-grid {

    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 18px;

    margin-bottom: 30px;

}


.stat-card {

    background: #FFFFFF;

    border:
        1px solid
        #E8E1D5;

    border-radius: 18px;

    padding: 22px;

    position: relative;

    overflow: hidden;

    transition: 0.2s;

}


.stat-card:hover {

    transform: translateY(-3px);

    box-shadow:
        0 12px 30px
        rgba(22,38,43,0.08);

}


.stat-card::after {

    content: "";

    position: absolute;

    width: 80px;

    height: 80px;

    border-radius: 50%;

    background:
        rgba(201,148,46,0.08);

    right: -25px;

    top: -25px;

}


.stat-icon {

    width: 45px;

    height: 45px;

    border-radius: 13px;

    display: flex;

    align-items: center;

    justify-content: center;

    background: #EFE7D6;

    font-size: 21px;

    margin-bottom: 17px;

}


.stat-label {

    color: #6C7778;

    font-size: 13px;

    margin-bottom: 7px;

}


.stat-value {

    color: #16262B;

    font-size: 22px;

    font-weight: 700;

}


.stat-sub {

    color: #8A7A4F;

    font-size: 11px;

    margin-top: 7px;

}


/* ============================================================
   TITRES DES SECTIONS
   ============================================================ */

.section-header {

    display: flex;

    align-items: center;

    justify-content: space-between;

    margin:
        28px
        0
        14px;

}


.section-title {

    font-family:
        'Fraunces',
        serif;

    color: #16262B;

    font-size: 25px;

    font-weight: 500;

}


.section-link {

    color: #8A7A4F;

    font-size: 13px;

}


/* ============================================================
   COMPTES
   ============================================================ */

.accounts-grid {

    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(350px, 1fr)
        );

    gap: 18px;

}


.account-card {

    background:
        linear-gradient(
            135deg,
            #203A43,
            #16262B
        );

    color: #FFFFFF;

    padding: 25px;

    border-radius: 20px;

    position: relative;

    overflow: hidden;

    min-height: 210px;

    box-shadow:
        0 15px 35px
        rgba(22,38,43,0.16);

}


.account-card::before {

    content: "";

    position: absolute;

    width: 230px;

    height: 230px;

    border-radius: 50%;

    border:
        1px solid
        rgba(201,148,46,0.25);

    right: -90px;

    top: -120px;

}


.account-card::after {

    content: "";

    position: absolute;

    width: 160px;

    height: 160px;

    border-radius: 50%;

    background:
        rgba(201,148,46,0.07);

    right: -55px;

    bottom: -80px;

}


.account-top {

    display: flex;

    align-items: center;

    justify-content: space-between;

    position: relative;

    z-index: 1;

}


.account-type {

    font-size: 14px;

    color: #D6E0E1;

}


.bank-chip {

    width: 42px;

    height: 31px;

    border-radius: 7px;

    background:
        linear-gradient(
            135deg,
            #D8B45A,
            #A77B20
        );

}


.account-balance-label {

    margin-top: 28px;

    color: #B7C4CB;

    font-size: 12px;

    position: relative;

    z-index: 1;

}


.account-balance {

    font-size: 29px;

    font-weight: 700;

    margin-top: 5px;

    color: #F6F2E9;

    position: relative;

    z-index: 1;

}


.account-iban {

    margin-top: 28px;

    color: #D7E0E4;

    font-size: 13px;

    letter-spacing: 0.7px;

    position: relative;

    z-index: 1;

}


/* ============================================================
   ACTIVITE
   ============================================================ */

.activity-card {

    background: #FFFFFF;

    border:
        1px solid
        #E8E1D5;

    border-radius: 18px;

    padding: 23px;

    margin-bottom: 28px;

}


.activity-row {

    display: flex;

    align-items: center;

    gap: 15px;

    padding: 14px 0;

    border-bottom:
        1px solid
        #F0ECE4;

}


.activity-row:last-child {

    border-bottom: none;

}


.activity-icon {

    width: 42px;

    height: 42px;

    border-radius: 12px;

    display: flex;

    align-items: center;

    justify-content: center;

    background: #EFE7D6;

    font-size: 18px;

}


.activity-info {

    flex: 1;

}


.activity-name {

    color: #16262B;

    font-size: 14px;

    font-weight: 600;

}


.activity-date {

    color: #899394;

    font-size: 11px;

    margin-top: 4px;

}


.activity-status {

    color: #5B9A72;

    background:
        rgba(91,154,114,0.10);

    padding: 6px 10px;

    border-radius: 20px;

    font-size: 11px;

    font-weight: 600;

}


/* ============================================================
   ASSISTANT HEADER
   ============================================================ */

.assistant-header {

    display: flex;

    align-items: center;

    gap: 12px;

    margin-bottom: 15px;

}


.assistant-logo {

    width: 52px;

    height: 52px;

    border-radius: 16px;

    background: #16262B;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 22px;

    box-shadow:
        0 8px 18px
        rgba(22,38,43,0.14);

}


.assistant-title {

    font-family:
        'Fraunces',
        serif;

    color: #16262B;

    font-size: 29px;

    font-weight: 500;

}


.assistant-subtitle {

    color: #7D8A8E;

    font-size: 12px;

    margin-top: 3px;

}


/* ============================================================
   CHAT BOX
   ============================================================ */

.chat-box {

    background: #FFFFFF;

    border-radius: 20px;

    border:
        1px solid
        #E8E1D5;

    padding: 24px;

    box-shadow:
        0 8px 25px
        rgba(22,38,43,0.04);

}


/* ============================================================
   CHAT THREAD
   CORRECTION :
   TOUJOURS COMMENCER EN HAUT
   ============================================================ */

.chat-thread {

    display: flex;

    flex-direction: column;

    justify-content: flex-start;

    align-items: stretch;

    gap: 16px;

    margin-bottom: 20px;

    min-height: 80px;

    max-height: 520px;

    overflow-y: auto;

    overflow-x: hidden;

    padding:
        5px
        8px
        10px
        2px;

    scroll-behavior: smooth;

}


/* ============================================================
   GROUPE QUESTION + REPONSE
   ============================================================ */

.conversation-pair {

    display: flex;

    flex-direction: column;

    align-items: stretch;

    gap: 10px;

    width: 100%;

}


/* ============================================================
   MESSAGES
   ============================================================ */

.msg {

    padding: 14px 18px;

    border-radius: 16px;

    width: fit-content;

    max-width: 82%;

    min-height: auto;

    height: auto;

    white-space: pre-wrap;

    word-break: break-word;

    overflow-wrap: anywhere;

    line-height: 1.55;

    font-size: 14px;

    display: flex;

    flex-direction: column;

    justify-content: flex-start;

}


.msg-question {

    align-self: flex-end;

    margin-left: auto;

    background: #16262B;

    color: #FFFFFF;

    border-bottom-right-radius: 4px;

    box-shadow:
        0 5px 15px
        rgba(22,38,43,0.10);

}


.msg-reponse {

    align-self: flex-start;

    margin-right: auto;

    background: #F1EBDD;

    color: #16262B;

    border-left:
        4px solid
        #C9942E;

    border-bottom-left-radius: 4px;

}


.msg-meta {

    font-size: 11px;

    font-weight: 600;

    opacity: 0.70;

    margin-bottom: 6px;

}


.question-text {

    white-space: pre-wrap;

    word-break: break-word;

}


/* ============================================================
   IMAGE DANS LE MESSAGE UTILISATEUR
   ============================================================ */

.chat-image-container {

    margin-top: 12px;

    width: 100%;

}


.chat-image-label {

    font-size: 11px;

    color: #D9C68C;

    margin-bottom: 7px;

    display: flex;

    align-items: center;

    gap: 5px;

}


.chat-image {

    display: block;

    width: 100%;

    max-width: 330px;

    max-height: 300px;

    object-fit: cover;

    border-radius: 12px;

    border:
        1px solid
        rgba(255,255,255,0.20);

    cursor: pointer;

}


/* ============================================================
   IMAGE SANS TEXTE
   ============================================================ */

.image-only-text {

    font-style: italic;

    color: #D7E0E4;

}


/* ============================================================
   MESSAGE VIDE
   ============================================================ */

.vide {

    color: #7D8A8E;

    font-size: 14px;

    padding: 25px 0;

    text-align: center;

    width: 100%;

}


/* ============================================================
   FORMULAIRE QUESTION
   ============================================================ */

.question-box {

    display: flex;

    gap: 10px;

    align-items: stretch;

}


.question-box input[type=text] {

    flex: 1;

    margin-bottom: 0;

    padding: 15px 17px;

    border:
        1px solid
        #DED8CB;

    border-radius: 12px;

    font-size: 14px;

    background: #FCFAF6;

    outline: none;

}


.question-box input[type=text]:focus {

    border-color: #C9942E;

    box-shadow:
        0 0 0 3px
        rgba(201,148,46,0.10);

}


.send-button {

    background: #16262B;

    color: #F6F2E9;

    border: none;

    padding: 0 25px;

    border-radius: 12px;

    cursor: pointer;

    font-size: 14px;

    font-weight: 600;

    transition: 0.2s;

}


.send-button:hover {

    background: #C9942E;

    color: #16262B;

}


/* ============================================================
   UPLOAD
   ============================================================ */

.upload-area {

    margin-top: 15px;

    border:
        1.5px dashed
        #D5C6A8;

    border-radius: 14px;

    background: #FCFAF6;

    padding: 14px 17px;

    display: flex;

    align-items: center;

    justify-content: space-between;

    transition: 0.2s;

}


.upload-area:hover {

    background: #F6F0E5;

    border-color: #C9942E;

}


.upload-text {

    display: flex;

    align-items: center;

    gap: 11px;

}


.upload-icon {

    width: 42px;

    height: 42px;

    background: #EFE7D6;

    border-radius: 12px;

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 18px;

}


.upload-main {

    color: #16262B;

    font-size: 13px;

    font-weight: 600;

}


.upload-sub {

    color: #899394;

    font-size: 11px;

    margin-top: 3px;

}


.upload-button {

    background: #EFE7D6;

    color: #16262B;

    padding: 11px 16px;

    border-radius: 10px;

    cursor: pointer;

    font-size: 12px;

    font-weight: 600;

    transition: 0.2s;

}


.upload-button:hover {

    background: #C9942E;

}


.file-input-hidden {

    display: none;

}


.file-name {

    margin-top: 8px;

    color: #8A7A4F;

    font-size: 12px;

}


/* ============================================================
   LOADING
   ============================================================ */

.loading {

    display: none;

    color: #8A7A4F;

    margin-top: 12px;

    font-size: 13px;

    background: #F6F0E5;

    padding: 10px 13px;

    border-radius: 9px;

}


/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 1000px) {

    .sidebar {

        width: 230px;

    }

    .main {

        margin-left: 230px;

        width:
            calc(100% - 230px);

        padding: 30px;

    }

    .stats-grid {

        grid-template-columns: 1fr;

    }

}


@media (max-width: 700px) {

    .sidebar {

        position: relative;

        width: 100%;

        height: auto;

    }

    .layout {

        flex-direction: column;

    }

    .main {

        margin-left: 0;

        width: 100%;

        padding:
            25px
            18px;

    }

    .dashboard-header {

        flex-direction: column;

        gap: 15px;

    }

    .accounts-grid {

        grid-template-columns: 1fr;

    }

    .question-box {

        flex-direction: column;

    }

    .send-button {

        padding: 15px;

    }

    .upload-area {

        align-items: flex-start;

        gap: 12px;

        flex-direction: column;

    }

    .msg {

        max-width: 95%;

    }

}

</style>
"""


# ============================================================
# PAGE LOGIN
# ============================================================

LOGIN_PAGE = STYLE + """

<div class="login-wrap">

    <div class="card">

        <div class="login-brand">

            <div class="login-logo">

                Hope<span>Bank</span>

            </div>

            <div class="login-subtitle">

                Votre espace bancaire sécurisé

            </div>

        </div>


        <form method="POST">

            <label>
                Identifiant (CIN)
            </label>

            <input
                type="text"
                name="identifiant"
                required
            >


            <label>
                Mot de passe
            </label>

            <input
                type="password"
                name="mot_de_passe"
                required
            >


            <input
                type="submit"
                value="Se connecter"
            >

        </form>


        {% if erreur %}

            <div class="erreur">

                {{ erreur }}

            </div>

        {% endif %}

    </div>

</div>
"""


# ============================================================
# DASHBOARD
# ============================================================

DASHBOARD_PAGE = STYLE + """

<div class="layout">


    <!-- ====================================================
         SIDEBAR
         ==================================================== -->

    <div class="sidebar">


        <div class="brand-box">

            <div class="brand-logo">

                Hope<span>Bank</span>

            </div>

            <div class="brand-line"></div>

        </div>



        <div class="user-box">

            <div class="user-avatar">

                {{ client['nom_complet'][0] }}

            </div>


            <div class="user-name">

                {{ client['nom_complet'] }}

            </div>


            <div class="user-role">

                Espace client

            </div>

        </div>



        <nav>


            <div class="nav-title">

                NAVIGATION

            </div>


            <a
                href="/accueil"
                class="nav-item"
            >

                <span class="nav-icon">
                    🏠
                </span>

                Accueil

            </a>


            <a
                href="/dashboard"
                class="nav-item actif"
            >

                <span class="nav-icon">
                    📊
                </span>

                Tableau de bord

            </a>


        </nav>



        <div class="sidebar-bottom">


            <div class="contact-mini">


                <div class="contact-mini-title">

                    BESOIN D'AIDE ?

                </div>


                <div class="contact-mini-text">

                    📞 58 311 751

                    <br>

                    ✉️ amalchourabi@esprit.tn

                </div>


            </div>



            <a
                href="/logout"
                class="logout-link"
            >

                🚪 Se déconnecter

            </a>


        </div>


    </div>



    <!-- ====================================================
         MAIN
         ==================================================== -->

    <div class="main">


        <!-- HEADER -->

        <div class="dashboard-header">


            <div>


                <div class="dashboard-eyebrow">

                    Espace personnel

                </div>


                <h1 class="dashboard-title">

                    Bonjour, {{ client['nom_complet'] }} 👋

                </h1>


                <div class="dashboard-date">

                    Voici un aperçu de votre situation bancaire.

                </div>


            </div>



            <div class="header-badge">


                <div class="status-dot"></div>

                Compte sécurisé


            </div>


        </div>



        <!-- =================================================
             STATISTIQUES
             ================================================= -->

        <div class="stats-grid">


            <div class="stat-card">


                <div class="stat-icon">

                    💳

                </div>


                <div class="stat-label">

                    Comptes actifs

                </div>


                <div class="stat-value">

                    {{ comptes|length }}

                </div>


                <div class="stat-sub">

                    Vos comptes HopeBank

                </div>


            </div>



            <div class="stat-card">


                <div class="stat-icon">

                    🏦

                </div>


                <div class="stat-label">

                    Statut bancaire

                </div>


                <div class="stat-value">

                    Actif

                </div>


                <div class="stat-sub">

                    Accès sécurisé

                </div>


            </div>



            <div class="stat-card">


                <div class="stat-icon">

                    🤖

                </div>


                <div class="stat-label">

                    Assistant

                </div>


                <div class="stat-value">

                    24 / 7

                </div>


                <div class="stat-sub">

                    Toujours disponible

                </div>


            </div>


        </div>



        <!-- =================================================
             COMPTES
             ================================================= -->

        <div class="section-header">


            <div class="section-title">

                Mes comptes

            </div>


            <div class="section-link">

                HopeBank · Espace sécurisé

            </div>


        </div>



        <div class="accounts-grid">


            {% for c in comptes %}


            <div class="account-card">


                <div class="account-top">


                    <div class="account-type">

                        {{ c['type_compte'] }}

                    </div>


                    <div class="bank-chip"></div>


                </div>



                <div class="account-balance-label">

                    SOLDE DISPONIBLE

                </div>



                <div class="account-balance">

                    {{ c['solde'] }} {{ c['devise'] }}

                </div>



                <div class="account-iban">

                    {{ c['iban'] }}

                </div>


            </div>


            {% endfor %}


        </div>



        <!-- =================================================
             ACTIVITE
             ================================================= -->

        <div class="section-header">


            <div class="section-title">

                Activité bancaire

            </div>


        </div>



        <div class="activity-card">


            <div class="activity-row">


                <div class="activity-icon">

                    🔐

                </div>


                <div class="activity-info">


                    <div class="activity-name">

                        Connexion sécurisée

                    </div>


                    <div class="activity-date">

                        Votre session est actuellement active

                    </div>


                </div>


                <div class="activity-status">

                    Sécurisé

                </div>


            </div>



            <div class="activity-row">


                <div class="activity-icon">

                    🏦

                </div>


                <div class="activity-info">


                    <div class="activity-name">

                        Consultation des comptes

                    </div>


                    <div class="activity-date">

                        Vos informations sont disponibles en temps réel

                    </div>


                </div>


                <div class="activity-status">

                    Disponible

                </div>


            </div>



            <div class="activity-row">


                <div class="activity-icon">

                    🤖

                </div>


                <div class="activity-info">


                    <div class="activity-name">

                        Assistant HopeBank

                    </div>


                    <div class="activity-date">

                        Posez vos questions concernant vos comptes

                    </div>


                </div>


                <div class="activity-status">

                    En ligne

                </div>


            </div>


        </div>



        <!-- =================================================
             ASSISTANT
             ================================================= -->

        <div class="assistant-header">


            <div class="assistant-logo">

                💬

            </div>


            <div>


                <div class="assistant-title">

                    Assistant HopeBank

                </div>


                <div class="assistant-subtitle">

                    Votre assistant bancaire intelligent

                </div>


            </div>


        </div>



        <div class="chat-box">


            <!-- ============================================
                 HISTORIQUE
                 ============================================ -->

            <div
                class="chat-thread"
                id="chat-thread"
            >


                {% if not historique %}


                    <div class="vide">

                        👋 Bonjour ! Je suis votre assistant HopeBank.

                        <br><br>

                        Posez-moi une question concernant vos comptes.

                    </div>


                {% endif %}



                {% for msg in historique %}


                    <div class="conversation-pair">


                        <!-- QUESTION UTILISATEUR -->

                        <div class="msg msg-question">


                            <div class="msg-meta">

                                Vous

                            </div>


                            {% if msg['question'] %}


                                <div class="question-text">

                                    {{ msg['question'] }}

                                </div>


                            {% else %}


                                <div class="image-only-text">

                                    Document envoyé

                                </div>


                            {% endif %}



                            <!-- IMAGE DANS LA QUESTION -->

                            {% if msg['image_url'] %}


                                <div class="chat-image-container">


                                    <div class="chat-image-label">

                                        📎 Document joint

                                    </div>


                                    <img
                                        src="{{ msg['image_url'] }}"
                                        class="chat-image"
                                        alt="Document envoyé"
                                        onclick="window.open(this.src, '_blank')"
                                    >


                                </div>


                            {% endif %}


                        </div>



                        <!-- REPONSE ASSISTANT -->

                        <div class="msg msg-reponse">


                            <div class="msg-meta">

                                Assistant HopeBank

                            </div>


                            {{ msg['reponse'] }}


                        </div>


                    </div>


                {% endfor %}


            </div>



            <!-- ============================================
                 FORMULAIRE
                 ============================================ -->

            <form
                method="POST"
                action="/question"
                enctype="multipart/form-data"
                onsubmit="showLoading()"
            >


                <div class="question-box">


                    <input
                        type="text"
                        name="question"
                        placeholder="Ex : Quel est mon solde actuel ?"
                    >


                    <button
                        type="submit"
                        class="send-button"
                    >

                        Envoyer →

                    </button>


                </div>



                <!-- ========================================
                     AJOUT DOCUMENT
                     ======================================== -->

                <div class="upload-area">


                    <div class="upload-text">


                        <div class="upload-icon">

                            📎

                        </div>


                        <div>


                            <div class="upload-main">

                                Ajouter un document

                            </div>


                            <div class="upload-sub">

                                Relevé bancaire, carte ou autre document

                            </div>


                        </div>


                    </div>



                    <label
                        for="image-upload"
                        class="upload-button"
                    >

                        Choisir un fichier

                    </label>



                    <input
                        id="image-upload"
                        class="file-input-hidden"
                        type="file"
                        name="image"
                        accept="image/*"
                        onchange="showFileName()"
                    >


                </div>



                <div
                    id="file-name"
                    class="file-name"
                ></div>


            </form>



            <div
                class="loading"
                id="loading"
            >

                ⏳ Traitement de votre demande en cours...

            </div>


        </div>


    </div>


</div>



<script>


function showFileName() {

    const input =
        document.getElementById(
            "image-upload"
        );


    const fileName =
        document.getElementById(
            "file-name"
        );


    if (
        input.files &&
        input.files.length > 0
    ) {

        fileName.innerText =
            "✓ " +
            input.files[0].name;

    }

    else {

        fileName.innerText = "";

    }

}



function showLoading() {

    document
        .getElementById("loading")
        .style
        .display = "block";

}



window.addEventListener(
    "load",
    function() {

        const chat =
            document.getElementById(
                "chat-thread"
            );


        if (chat) {

            chat.scrollTop =
                chat.scrollHeight;

        }

    }
);


</script>
"""


# ============================================================
# STYLE PAGE ACCUEIL
# ============================================================

STYLE_ACCUEIL = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=DM+Sans:wght@400;500;600;700&display=swap');

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html {
    scroll-behavior: smooth;
}

body {
    margin: 0;
}

.ha-body {
    background:
        radial-gradient(circle at 92% 8%, rgba(201,148,46,0.12), transparent 25%),
        #F6F2E9;
    color: #16262B;
    min-height: 100vh;
    font-family: 'DM Sans', Arial, sans-serif;
    overflow-x: hidden;
}

/* ============================================================
   NAVBAR
   ============================================================ */

.ha-nav {
    max-width: 1400px;
    margin: 0 auto;
    padding: 24px 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.ha-logo {
    font-family: 'Fraunces', serif;
    font-size: 27px;
    font-weight: 600;
    color: #16262B;
    text-decoration: none;
    letter-spacing: 0.2px;
}

.ha-logo span {
    color: #C9942E;
}

.ha-nav-cta {
    background: #16262B;
    color: #F6F2E9;
    text-decoration: none;
    padding: 13px 23px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 700;
    transition: 0.25s ease;
    box-shadow: 0 8px 22px rgba(22,38,43,0.12);
}

.ha-nav-cta:hover {
    background: #C9942E;
    color: #16262B;
    transform: translateY(-2px);
}

/* ============================================================
   HERO
   ============================================================ */

.ha-hero {
    max-width: 1280px;
    margin: 0 auto;
    padding: 35px 60px 75px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 60px;
    align-items: center;
}

.ha-hero h1 {
    font-family: 'Fraunces', serif;
    font-weight: 500;
    font-size: 58px;
    line-height: 1.08;
    color: #16262B;
    max-width: 11.5ch;
}

.ha-hero .accent-line {
    color: #C9942E;
    font-style: italic;
}

.ha-hero p.lede {
    font-size: 17px;
    line-height: 1.65;
    color: #46565B;
    max-width: 48ch;
    margin: 24px 0 31px;
}

.ha-hero-actions {
    display: flex;
    align-items: center;
    gap: 22px;
    flex-wrap: wrap;
}

.ha-btn-primary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #C9942E;
    color: #16262B;
    text-decoration: none;
    font-weight: 700;
    padding: 15px 23px;
    border-radius: 10px;
    transition: 0.25s ease;
}

.ha-btn-primary:hover {
    background: #B98320;
    color: #FFFFFF;
    transform: translateY(-2px);
    box-shadow: 0 12px 25px rgba(201,148,46,0.25);
}

.ha-btn-ghost {
    color: #46565B;
    text-decoration: none;
    font-size: 14px;
    font-weight: 600;
    padding: 14px 0;
    border-bottom: 1px solid #C9942E;
    transition: 0.2s;
}

.ha-btn-ghost:hover {
    color: #C9942E;
}

/* ============================================================
   CARROUSEL PHOTOS BANCAIRES
   ============================================================ */

.bank-slider {
    position: relative;
    width: 100%;
    height: 430px;
    border-radius: 28px;
    overflow: hidden;
    background: #203A43;
    box-shadow: 0 25px 60px rgba(22,38,43,0.18);
}

.bank-slide {
    position: absolute;
    inset: 0;
    opacity: 0;
    transform: scale(1.05);
    transition:
        opacity 0.9s ease,
        transform 5s ease;
}

.bank-slide.active {
    opacity: 1;
    transform: scale(1);
    z-index: 2;
}

.bank-slide img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

.bank-slide-overlay {
    position: absolute;
    inset: 0;
    background:
        linear-gradient(
            180deg,
            rgba(22,38,43,0.05) 25%,
            rgba(22,38,43,0.78) 100%
        );
}

.bank-slide-caption {
    position: absolute;
    left: 30px;
    right: 30px;
    bottom: 30px;
    z-index: 3;
    color: #FFFFFF;
}

.bank-slide-caption small {
    display: inline-block;
    color: #E8C77D;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.bank-slide-caption h3 {
    font-family: 'Fraunces', serif;
    font-size: 29px;
    font-weight: 500;
    line-height: 1.15;
}

.slider-dots {
    position: absolute;
    z-index: 10;
    top: 24px;
    right: 24px;
    display: flex;
    gap: 7px;
}

.slider-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    border: none;
    background: rgba(255,255,255,0.45);
    padding: 0;
    cursor: pointer;
    transition: 0.25s ease;
}

.slider-dot.active {
    width: 26px;
    border-radius: 20px;
    background: #C9942E;
}

.slider-badge {
    position: absolute;
    z-index: 10;
    left: 24px;
    top: 24px;
    background: rgba(246,242,233,0.93);
    color: #16262B;
    backdrop-filter: blur(8px);
    padding: 10px 14px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: 700;
}

/* ============================================================
   TRUST
   ============================================================ */

.ha-trust {
    border-top: 1px solid #E4DDC9;
    border-bottom: 1px solid #E4DDC9;
}

.ha-trust-inner {
    max-width: 1280px;
    margin: 0 auto;
    padding: 28px 60px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 30px;
}

.ha-trust-num {
    font-family: 'Fraunces', serif;
    font-size: 24px;
    font-weight: 600;
    color: #16262B;
    margin-bottom: 5px;
}

.ha-trust-label {
    font-size: 13px;
    color: #6C7778;
}

/* ============================================================
   SERVICES
   ============================================================ */

.ha-services {
    max-width: 1280px;
    margin: 0 auto;
    padding: 85px 60px;
}

.ha-services h2 {
    font-family: 'Fraunces', serif;
    font-weight: 500;
    font-size: 35px;
    color: #16262B;
    max-width: 17ch;
    margin-bottom: 40px;
}

.ha-bento {
    display: grid;
    grid-template-columns: 1.4fr 1fr;
    grid-template-rows: auto auto;
    gap: 20px;
}

.ha-card {
    background: #FFFFFF;
    border: 1px solid #ECE5D8;
    border-radius: 18px;
    padding: 31px;
    transition: 0.25s ease;
}

.ha-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 35px rgba(22,38,43,0.08);
}

.ha-card-feature {
    grid-row: span 2;
    background: #EFE7D6;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.ha-card-icon {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #FFFFFF;
    border-radius: 14px;
    font-size: 23px;
    margin-bottom: 22px;
}

.ha-card h3 {
    font-size: 18px;
    margin-bottom: 10px;
    color: #16262B;
}

.ha-card-feature h3 {
    font-family: 'Fraunces', serif;
    font-weight: 500;
    font-size: 28px;
    margin-bottom: 13px;
}

.ha-card p {
    font-size: 14.5px;
    color: #46565B;
    line-height: 1.6;
}

/* ============================================================
   CTA + FOOTER
   ============================================================ */

.ha-cta {
    max-width: 1280px;
    margin: 0 auto 90px;
    padding: 0 60px;
}

.ha-cta-inner {
    background:
        radial-gradient(circle at 90% 20%, rgba(201,148,46,0.22), transparent 28%),
        #203A43;
    border-radius: 22px;
    padding: 56px 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 30px;
}

.ha-cta-inner h2 {
    font-family: 'Fraunces', serif;
    font-weight: 500;
    font-size: 30px;
    color: #FFFFFF;
    max-width: 18ch;
}

.ha-footer {
    border-top: 1px solid #E4DDC9;
    padding: 28px 60px;
    display: flex;
    justify-content: space-between;
    gap: 20px;
    color: #7D8A8E;
    font-size: 13px;
    max-width: 1280px;
    margin: 0 auto;
}

.ha-footer a {
    color: #7D8A8E;
    text-decoration: none;
}

.ha-footer a:hover {
    color: #C9942E;
}

/* ============================================================
   RESPONSIVE
   ============================================================ */

@media (max-width: 900px) {

    .ha-nav,
    .ha-hero,
    .ha-trust-inner,
    .ha-services,
    .ha-cta,
    .ha-footer {
        padding-left: 25px;
        padding-right: 25px;
    }

    .ha-hero {
        grid-template-columns: 1fr;
        gap: 40px;
        padding-top: 20px;
    }

    .ha-hero h1 {
        font-size: 46px;
    }

    .bank-slider {
        height: 390px;
    }

    .ha-trust-inner,
    .ha-bento {
        grid-template-columns: 1fr;
    }

    .ha-card-feature {
        grid-row: auto;
    }

    .ha-cta-inner {
        flex-direction: column;
        align-items: flex-start;
    }

    .ha-footer {
        flex-direction: column;
    }
}

@media (max-width: 560px) {

    .ha-nav {
        padding-top: 18px;
        padding-bottom: 18px;
    }

    .ha-logo {
        font-size: 23px;
    }

    .ha-nav-cta {
        padding: 10px 13px;
        font-size: 12px;
    }

    .ha-hero h1 {
        font-size: 39px;
    }

    .ha-hero p.lede {
        font-size: 15px;
    }

    .bank-slider {
        height: 320px;
        border-radius: 20px;
    }

    .bank-slide-caption h3 {
        font-size: 23px;
    }

    .ha-trust-inner {
        grid-template-columns: 1fr;
        gap: 18px;
    }
}

</style>
"""


# ============================================================
# PAGE ACCUEIL
# ============================================================

HOME_PAGE = STYLE_ACCUEIL + """
<div class="ha-body">

    <!-- NAVBAR -->
    <div class="ha-nav">

        <a href="/accueil" class="ha-logo">
            Hope<span>Bank</span>
        </a>

        <a href="/dashboard" class="ha-nav-cta">
            Accéder à mon compte
        </a>

    </div>


    <!-- HERO -->
    <div class="ha-hero">

        <!-- TEXTE -->
        <div>

            <h1>
                Une banque qui avance
                <br>
                quand
                <span class="accent-line">vous</span>
                avancez.
            </h1>

            <p class="lede">
                HopeBank associe le suivi bancaire au quotidien
                à un assistant qui répond à vos questions sur vos comptes,
                en clair et à toute heure — sans jargon,
                sans file d'attente.
            </p>

            <div class="ha-hero-actions">

                <a href="/dashboard" class="ha-btn-primary">
                    Accéder à mon compte
                </a>

                <a href="#services" class="ha-btn-ghost">
                    Découvrir nos services
                </a>

            </div>

        </div>


        <!-- CARROUSEL DE PHOTOS -->
        <div class="bank-slider" id="bank-slider">

            <div class="slider-badge">
                ✦ HopeBank
            </div>

            <div class="slider-dots">
                <button class="slider-dot active" type="button" aria-label="Photo 1"></button>
                <button class="slider-dot" type="button" aria-label="Photo 2"></button>
                <button class="slider-dot" type="button" aria-label="Photo 3"></button>
                <button class="slider-dot" type="button" aria-label="Photo 4"></button>
                <button class="slider-dot" type="button" aria-label="Photo 5"></button>
            </div>


            <!--
                AJOUTEZ VOS PROPRES IMAGES ICI :

                static/images/bank1.jpg
                static/images/bank2.jpg
                static/images/bank3.jpg
                static/images/bank4.jpg
                static/images/bank5.jpg
            -->

            <div class="bank-slide active">

                <img
                    src="/static/images/bank1.jpg"
                    alt="Services bancaires"
                >

                <div class="bank-slide-overlay"></div>

                <div class="bank-slide-caption">
                    <small>Votre banque</small>
                    <h3>Simple, moderne et proche de vous.</h3>
                </div>

            </div>


            <div class="bank-slide">

                <img
                    src="/static/images/bank2.jpg"
                    alt="Paiement et carte bancaire"
                >

                <div class="bank-slide-overlay"></div>

                <div class="bank-slide-caption">
                    <small>Paiements</small>
                    <h3>Gardez le contrôle de vos finances.</h3>
                </div>

            </div>


            <div class="bank-slide">

                <img
                    src="/static/images/bank3.jpg"
                    alt="Banque digitale"
                >

                <div class="bank-slide-overlay"></div>

                <div class="bank-slide-caption">
                    <small>Digital</small>
                    <h3>Vos comptes accessibles en toute simplicité.</h3>
                </div>

            </div>


            <div class="bank-slide">

                <img
                    src="/static/images/bank4.jpg"
                    alt="Épargne"
                >

                <div class="bank-slide-overlay"></div>

                <div class="bank-slide-caption">
                    <small>Épargne</small>
                    <h3>Construisez vos projets, étape par étape.</h3>
                </div>

            </div>


            <div class="bank-slide">

                <img
                    src="/static/images/bank5.jpg"
                    alt="Innovation bancaire"
                >

                <div class="bank-slide-overlay"></div>

                <div class="bank-slide-caption">
                    <small>Innovation</small>
                    <h3>Une expérience bancaire pensée pour demain.</h3>
                </div>

            </div>

        </div>

    </div>


    <!-- INFORMATIONS -->
    <div class="ha-trust">

        <div class="ha-trust-inner">

            <div>
                <div class="ha-trust-num">24/7</div>
                <div class="ha-trust-label">
                    Un assistant disponible à tout moment
                </div>
            </div>

            <div>
                <div class="ha-trust-num">Simple</div>
                <div class="ha-trust-label">
                    Vos informations bancaires en un seul espace
                </div>
            </div>

            <div>
                <div class="ha-trust-num">TND</div>
                <div class="ha-trust-label">
                    Comptes en dinar tunisien
                </div>
            </div>

        </div>

    </div>


    <!-- SERVICES -->
    <div class="ha-services" id="services">

        <h2>
            Le nécessaire, sans le superflu.
        </h2>

        <div class="ha-bento">

            <div class="ha-card ha-card-feature">

                <div class="ha-card-icon">🏦</div>

                <h3>
                    Vos comptes, en clair
                </h3>

                <p>
                    Soldes, IBAN et informations bancaires
                    présentés simplement pour voir ce qui compte
                    en un coup d'œil.
                </p>

            </div>


            <div class="ha-card">

                <div class="ha-card-icon">💬</div>

                <h3>
                    Assistant intelligent
                </h3>

                <p>
                    Posez une question concernant votre compte
                    et obtenez une réponse contextualisée.
                </p>

            </div>


            <div class="ha-card">

                <div class="ha-card-icon">📄</div>

                <h3>
                    Documents analysés
                </h3>

                <p>
                    Joignez un relevé ou un document à votre
                    question pour faciliter son analyse.
                </p>

            </div>

        </div>

    </div>


    <!-- CTA -->
    <div class="ha-cta">

        <div class="ha-cta-inner">

            <h2>
                Votre espace client vous attend.
            </h2>

            <a href="/dashboard" class="ha-btn-primary">
                Accéder à mon compte
            </a>

        </div>

    </div>


    <!-- FOOTER -->
    <div class="ha-footer">

        <span>
            © 2026 HopeBank — Tunis, Tunisie
        </span>

        <span>

            <a href="tel:+21658311751">
                📞 58 311 751
            </a>

            &nbsp;·&nbsp;

            <a href="mailto:amalchourabi@esprit.tn">
                ✉️ amalchourabi@esprit.tn
            </a>

        </span>

    </div>

</div>


<script>

document.addEventListener(
    "DOMContentLoaded",
    function() {

        const slides =
            document.querySelectorAll(".bank-slide");

        const dots =
            document.querySelectorAll(".slider-dot");

        let currentSlide = 0;


        function showSlide(index) {

            slides.forEach(
                function(slide) {

                    slide.classList.remove("active");

                }
            );


            dots.forEach(
                function(dot) {

                    dot.classList.remove("active");

                }
            );


            slides[index].classList.add("active");

            dots[index].classList.add("active");

            currentSlide = index;

        }


        function nextSlide() {

            let next =
                currentSlide + 1;

            if (
                next >= slides.length
            ) {
                next = 0;
            }

            showSlide(next);

        }


        let sliderInterval =
            setInterval(
                nextSlide,
                4000
            );


        dots.forEach(
            function(dot, index) {

                dot.addEventListener(
                    "click",
                    function() {

                        showSlide(index);

                        clearInterval(
                            sliderInterval
                        );

                        sliderInterval =
                            setInterval(
                                nextSlide,
                                4000
                            );

                    }
                );

            }
        );

    }
);

</script>
"""


# ============================================================
# ACCUEIL
# ============================================================

@app.route("/accueil")
def accueil():

    return render_template_string(
        HOME_PAGE
    )


# ============================================================
# LOGIN
# ============================================================

@app.route("/", methods=["GET", "POST"])
def login():

    if "client_id" in session:

        return redirect(
            url_for("dashboard")
        )


    if request.method == "POST":


        identifiant = request.form["identifiant"]

        mot_de_passe = request.form["mot_de_passe"]


        conn = get_db()


        user = conn.execute(

            """
            SELECT *
            FROM utilisateurs
            WHERE identifiant = ?
            """,

            (identifiant,)

        ).fetchone()


        conn.close()



        if user and check_password_hash(

            user["mot_de_passe_hash"],

            mot_de_passe

        ):


            session["client_id"] = user["client_id"]

            session["historique"] = []


            return redirect(
                url_for("dashboard")
            )



        else:


            return render_template_string(

                LOGIN_PAGE,

                erreur=
                "Identifiant ou mot de passe incorrect."

            )


    return render_template_string(

        LOGIN_PAGE,

        erreur=None

    )


# ============================================================
# RECUPERER CLIENT ET COMPTES
# ============================================================

def get_client_comptes():


    conn = get_db()


    client = conn.execute(

        """
        SELECT *
        FROM clients
        WHERE id = ?
        """,

        (
            session["client_id"],
        )

    ).fetchone()



    comptes = conn.execute(

        """
        SELECT *
        FROM comptes
        WHERE client_id = ?
        """,

        (
            session["client_id"],
        )

    ).fetchall()



    conn.close()


    return client, comptes


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():


    if "client_id" not in session:

        return redirect(
            url_for("login")
        )


    client, comptes = get_client_comptes()


    historique = session.get(

        "historique",

        []

    )


    return render_template_string(

        DASHBOARD_PAGE,

        client=client,

        comptes=comptes,

        historique=historique

    )


# ============================================================
# QUESTION ASSISTANT
# ============================================================

@app.route(
    "/question",
    methods=["POST"]
)
def question():


    if "client_id" not in session:

        return redirect(
            url_for("login")
        )


    question_texte = request.form.get(

        "question",

        ""

    ).strip()



    fichier_image = request.files.get(
        "image"
    )



    # ========================================================
    # VERIFICATION IMAGE
    # ========================================================

    a_image = bool(

        fichier_image

        and

        fichier_image.filename

    )



    # ========================================================
    # SI RIEN N'EST ENVOYE
    # ========================================================

    if not question_texte and not a_image:

        return redirect(
            url_for("dashboard")
        )



    client, comptes = get_client_comptes()



    # ========================================================
    # CONTEXTE CLIENT
    # ========================================================

    contexte = f"""

Client :
{client['nom_complet']}

CIN :
{client['cin']}

Comptes :

"""



    for c in comptes:


        contexte += f"""

- IBAN : {c['iban']}
- Type : {c['type_compte']}
- Solde : {c['solde']} {c['devise']}

"""



    # ========================================================
    # VARIABLES IMAGE
    # ========================================================

    image_url = None

    image_data = None



    # ========================================================
    # TRAITEMENT IMAGE
    # ========================================================

    if a_image:


        # Lire les données pour Ollama

        image_bytes = fichier_image.read()


        image_data = base64.b64encode(

            image_bytes

        ).decode()



        # Remettre le curseur au début

        fichier_image.seek(0)



        # Nom sécurisé

        original_filename = secure_filename(

            fichier_image.filename

        )


        extension = os.path.splitext(

            original_filename

        )[1]


        # Nom unique

        unique_filename = (

            str(uuid.uuid4())

            +

            extension

        )


        # Chemin complet

        save_path = os.path.join(

            app.config["UPLOAD_FOLDER"],

            unique_filename

        )


        # Sauvegarder l'image

        with open(

            save_path,

            "wb"

        ) as f:

            f.write(
                image_bytes
            )


        # URL pour l'affichage HTML

        image_url = url_for(

            "static",

            filename=
            "uploads/" +
            unique_filename

        )



    # ========================================================
    # APPEL IA
    # ========================================================

    try:


        # ----------------------------------------------------
        # QUESTION AVEC IMAGE
        # ----------------------------------------------------

        if a_image:


            if question_texte:


                prompt_final = f"""

Voici la question du client :

{question_texte}

Réponds clairement à cette question en tenant compte de l'image envoyée.

"""


            else:


                prompt_final = """

Analyse le document ou l'image envoyé(e) et explique clairement son contenu au client.

"""


            response = requests.post(

                "http://localhost:11434/api/generate",

                json={

                    "model":
                    "banque-assistant-image",

                    "prompt":
                    prompt_final,

                    "images":
                    [image_data],

                    "stream":
                    False,

                    "keep_alive":
                    OLLAMA_KEEP_ALIVE,

                    "options": {
                        "num_ctx": OLLAMA_NUM_CTX,
                        "num_predict": OLLAMA_NUM_PREDICT
                    }

                },

                timeout=120

            )



        # ----------------------------------------------------
        # QUESTION TEXTE
        # ----------------------------------------------------

        else:


            prompt_complet = f"""

Voici les informations du client concerné :

{contexte}

Question du client :

{question_texte}

Réponds dans la même langue que la question.

"""


            response = requests.post(

                "http://localhost:11434/api/generate",

                json={

                    "model":
                    "banque-assistant-texte",

                    "prompt":
                    prompt_complet,

                    "stream":
                    False,

                    "keep_alive":
                    OLLAMA_KEEP_ALIVE,

                    "options": {
                        "num_ctx": OLLAMA_NUM_CTX,
                        "num_predict": OLLAMA_NUM_PREDICT
                    }

                },

                timeout=120

            )



        reponse_json = response.json()


        reponse_ia = reponse_json.get(

            "response",

            "Je n'ai pas pu générer une réponse."

        )


    except requests.exceptions.Timeout:


        reponse_ia = (

            "Le modèle a mis trop de temps à répondre. "

            "Réessayez avec une question plus courte."

        )



    except Exception as e:


        reponse_ia = (

            "Erreur lors du traitement : "

            +

            str(e)

        )



    # ========================================================
    # HISTORIQUE
    # ========================================================

    historique = session.get(

        "historique",

        []

    )



    historique.append({


        "question":

        question_texte,


        "reponse":

        reponse_ia,


        "image_url":

        image_url


    })



    # Limiter l'historique

    if len(historique) > 10:

        historique = historique[-10:]



    session["historique"] = historique



    # ========================================================
    # RETOUR DASHBOARD
    # ========================================================

    return redirect(
        url_for("dashboard")
    )


# ============================================================
# DECONNEXION
# ============================================================

@app.route("/logout")
def logout():


    session.clear()


    return redirect(
        url_for("accueil")
    )


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        port=5000

    )