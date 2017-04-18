#!venv/bin/python
import os
import sys
import json
from collections import namedtuple
import requests
import datetime
import click
import yaml

from app import create_app
from flask import current_app
from flask.cli import FlaskGroup
from flask_gnupg import fetch_gpg_key
from app import db
from app.models import User, Organization, IpRange, Fqdn, Asn, Email
from app.models import OrganizationGroup, Vulnerability, Tag
from app.models import ContactEmail, emails_organizations, tags_vulnerabilities
from app.models import Role, ReportType, OrganizationMembership, MembershipRole
from app.fixtures import testfixture

def create_cli_app(info):
    return create_app(os.getenv('DO_CONFIG') or 'default')


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@click.group(cls=FlaskGroup, create_app=create_cli_app)
def cli():
    """DO portal management script"""


@cli.command()
def addyaml():
   """Add sample data from yaml file""" 
   testfixture.testdata.addyaml()
   db.session.commit()    

@cli.command()
def add():
    """Add sample data"""

    cert = Organization(
        abbreviation="CERT",
        full_name="CERT Master User",
    )
    db.session.add(cert)

    cert_user = User(
        name = "cert master user",
    )
    cert_user.password = 'bla'
    db.session.add(cert_user)
    
    cert_user4cert = OrganizationMembership(
        email = 'certifant@cert.at',
        zip = '1234',
        organization = cert,        
        user = cert_user
    )
       
    db.session.commit()    
    
    click.echo('Done Org id: ' + str(cert.id)) 
    click.echo('Done User id: ' + str(cert_user.id)) 
    click.echo('adding sub org') 

    evn = Organization(
        abbreviation="EVN",
        full_name="EVN Dach",
        parent_org = cert
    )
    # db.session.add(evn)

    evn_user = User(
        name = "evn master user"
    )
    evn_user.password = 'bla'
    
    OrganizationMembership(
        email = 'master@evn.at',
        zip = '5678',
        organization = evn,        
        user = evn_user
    )

    evn_strom = Organization(
        abbreviation="EVN Strom",
        full_name="EVN Strom",
        parent_org = evn
    )
    db.session.add(evn_strom)

    evn_strom_user = User(
        name = "evn strom user",
    )
    evn_strom_user.password = 'bla'
    db.session.add(evn_strom_user)
    
    evnstrom_orguser = OrganizationMembership(
        email = 'strom@evn.at',
        zip = '5678',
        organization = evn_strom,        
        user = evn_strom_user
    )
    db.session.commit()    
    

@cli.command()
def delete():
    """delete sample data"""
    OrganizationMembership.query.delete()
    User.query.filter(User.name != 'testadmin').delete()
    Organization.query.filter(Organization.abbreviation != "CERT-EU").delete()
    db.session.commit()

@cli.command()
def print():
   """output sample data"""
   u = User.query.filter_by(name="certmaster").first()
   click.echo(u.name + str(u.id))
   for uo in u.user_memberships:
       click.echo(uo.email)
       click.echo(uo)
       click.echo(uo.organization.full_name)
       for co in uo.organization.child_organizations:
          click.echo(co.full_name)

   click.echo('**** organization_memberships ******')
   for oxu in u.get_organization_memberships():
   
       click.echo('%s %s %s' % 
           (oxu.email, oxu.membership_role.name,  oxu.organization.full_name))

   #click.echo(u.org_ids)

   click.echo('**** organization_memberships ******')
   oms = User.query.filter_by(name = 'Verbund Admin').first().get_organization_memberships()  
   if (oms):
     for oxu in oms: 
       click.echo('%s %s %s' % 
          (oxu.email, oxu.membership_role.name,  oxu.organization.full_name))

   click.echo('**** organizations ******')
   orgs = u.get_organizations()
   i = 0
   for org in orgs:
       click.echo(u.id)
       click.echo('%d %s %s' % 
           (i, org.full_name, org.abbreviation))
       i += 1

   click.echo('**** permission checks ******')
   evn_user = User.query.filter_by(name = 'EVN User').first()
   evnmaster = User.query.filter_by(name = 'evnmaster').first()
   click.echo("evnmaster for EVN %s \nEVN for evnmaster %s" %
        (evnmaster.may_handle_user(evn_user), evn_user.may_handle_user(evnmaster)))
   click.echo("cert for EVN %s \nEVN for cert %s" %
        (u.may_handle_user(evn_user), evn_user.may_handle_user(u)))
   click.echo("cert for evnmaster %s \nevnmaster for cert %s" %
        (u.may_handle_user(evnmaster), evnmaster.may_handle_user(u)))


   click.echo('**** user.get_userss ******')
   users = u.get_users()
   for user in users:
      click.echo("%s" % (user.name))
   
   click.echo('**** user.get_users(evnmaster) ******')
   users = evnmaster.get_users()
   for user in users:
      click.echo("%s" % (user.name))
  

if __name__ == '__main__':
    cli()
