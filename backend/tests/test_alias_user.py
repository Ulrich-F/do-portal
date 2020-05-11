from flask import url_for
from .conftest import assert_msg
from app.models import User

def test_return_users(client):
    rv = client.get(url_for('cp.get_cp_users'))
    #fuer lesbarkeit vorerst auskommentiert
    #assert_msg(rv, key='users')
    #liefert Liste der Datensaetze
    got = list(rv.json.values())
    #noch nicht ganz klar: [0][0], weil bei xyz.query.all() ein orm objekt herauskommt. orm noch genauer anschauen!!!
    some_entry = got[0][0]

    #einzelne zeile nochmal fetchen, die vorher in some_entry zugewiesen wurde.
    rv = client.get(url_for('cp.get_cp_user', user_id=some_entry['id']))
    #Ist unique, deshalb bei der Nachricht verwendet
    #assert_msg(rv, key='_email')
    single_entry = rv.json
    #einfach irgendwas vergleichen vorerst
    assert some_entry['name'] == single_entry['name']

