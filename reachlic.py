#
# by Brandon Frelich (b.frelich@f5.com)
# This comes with no warranty whatsoever.
#

import argparse
import requests
import json
import difflib

requests.packages.urllib3.disable_warnings()

parser = argparse.ArgumentParser(description='F5 BIG-IQ License Manager Utilities for Reachable BIG-IP devices')
parser.add_argument('--bigiq_ip', help='F5 BIG-IQ IP Address', required=True)
parser.add_argument('--bigiq_adm', help='F5 BIG-IQ admin username', required=True)
parser.add_argument('--bigiq_pwd', help='F5 BIG-IQ admin password', required=True)
parser.add_argument('--bigip_ip', help='F5 BIG-IP IP Address', required=True)
parser.add_argument('--bigip_user', help='F5 BIG-IP administrator level user', default="admin", required=False)
parser.add_argument('--bigip_pass', help='F5 BIG-IP administrator level password', default="admin", required=False)
parser.add_argument('--bigip_mac', help='F5 BIG-IP Unique MAC Address', required=False)
parser.add_argument("--use_mac", default=False, help='Use the BIG-IP MAC Address for the license filename', action='store_true', required=False)
parser.add_argument('--tenant_desc', help='The Machine Tenant ID/Description in double quotes', default="", required=False)
parser.add_argument('--hyper', help='The host hypervisor', default="Xen", required=False)
parser.add_argument('--sku1', help='BIG-IP License SKU Keyword #1 of two allowed', default="", required=False)
parser.add_argument('--sku2', help='BIG-IP License SKU Keyword #2 of two allowed', default="", required=False)
parser.add_argument('--action', help='F5 license manager actions (unreachable_license, unmanaged_license, managed_license', required=True)
parser.add_argument('--pool', help='BIG-IQ license pool name', default="my-pool", required=False)

headers = {
  'Content-Type': 'application/json'
}

####################################
# Function: Generate X-F5-Auth-Token
####################################
def bigiq_authtoken (ip,username,password):
  url = 'https://'+ip+'/mgmt/shared/authn/login'
  payload = {
    'username': username,
    'password': password
  }
  resp = requests.post(url,headers=headers, data=json.dumps(payload), verify=False)
  json_data =  json.loads(resp.text)
  return json_data['token']['token'];


###############################################
# Function: License Unreachable BIG-IP Device
###############################################
#https://{{bigiq_mgmt}}/mgmt/cm/device/tasks/licensing/pool/member-management
def unreachable_license(auth_token,ip,bip,bmac,useMAC,tenantName,hypervisor,sku1,sku2,poolName):
  url = 'https://'+ip+'/mgmt/cm/device/tasks/licensing/pool/member-management'
  headers = {
    'Content-Type': 'application/json',
    'X-F5-Auth-Token': auth_token
  }
  payload = {
      "licensePoolName": poolName,
      "command": "assign",
      "address": bip,
      "assignmentType": "UNREACHABLE",
      "macAddress": bmac,
      "hypervisor": hypervisor,
      "tenant": tenantName,
      "skuKeyword1": sku1,
      "skuKeyword2": sku2
    }
  resp = requests.post(url,headers=headers, data=json.dumps(payload), verify=False)
  json_data = json.loads(resp.text)
  id = json_data['id']
 # hypervisor = json_data['hypervisor']
 # print id
 # print hypervisor

 # licTxt = checkLicStatus(auth_token,ip,id)
 # print licTxt

#  if useMAC:
#    f=open(bmac+'_bigip.license', 'w+')
#    f.write(licTxt)
#  else:
#    f=open('bigip.license', 'w')
#    f.write(licTxt)
  return

###############################################
# Function: License Managed BIG-IP Device
###############################################
#https://{{bigiq_mgmt}}/mgmt/cm/device/tasks/licensing/pool/member-management
def managed_license(auth_token,ip,bip,tenantName,sku1,sku2,poolName):
  url = 'https://'+ip+'/mgmt/cm/device/tasks/licensing/pool/member-management'
  headers = {
    'Content-Type': 'application/json',
    'X-F5-Auth-Token': auth_token
  }

  payload = {
     "licensePoolName": poolName,
     "command": "assign",
     "unitOfMeasure": "yearly",
     "address": bip,
     "skuKeyword1": sku1,
     "skuKeyword2": sku2
  }
  resp = requests.post(url,headers=headers, data=json.dumps(payload), verify=False)
  json_data = json.loads(resp.text)
  id = json_data['id']
 # hypervisor = json_data['hypervisor']
 # print id
 # print hypervisor

  licTxt = checkLicStatus(auth_token,ip,id)
  print licTxt

#  if useMAC:
#    f=open(bmac+'_bigip.license', 'w+')
#    f.write(licTxt)
#  else:
#    f=open('bigip.license', 'w')
#    f.write(licTxt)
  return

###############################################
# Function: License Unmanaged BIG-IP Device
###############################################
#https://{{bigiq_mgmt}}/mgmt/cm/device/tasks/licensing/pool/member-management
def unmanaged_license(auth_token,ip,bip,bipuser,bippass,tenantName,sku1,sku2,poolName):
  url = 'https://'+ip+'/mgmt/cm/device/tasks/licensing/pool/member-management'
  headers = {
    'Content-Type': 'application/json',
    'X-F5-Auth-Token': auth_token
  }

  payload = {
     #"licensePoolName": "byol-pool-utility",
     "licensePoolName": poolName,
     "command": "assign",
     "unitOfMeasure": "yearly",
     "address": bip,
     "user": bipuser,
     "password": bippass,
     "skuKeyword1": sku1,
     "skuKeyword2": sku2
  }
  resp = requests.post(url,headers=headers, data=json.dumps(payload), verify=False)
  json_data = json.loads(resp.text)
  id = json_data['id']
 # hypervisor = json_data['hypervisor']
 # print id
 # print hypervisor

  licTxt = checkLicStatus(auth_token,ip,id)
  print licTxt

#  if useMAC:
#    f=open(bmac+'_bigip.license', 'w+')
#    f.write(licTxt)
#  else:
#    f=open('bigip.license', 'w')
#    f.write(licTxt)
  return


###################################################
# Function: Poll BIG-IQ for license issuance status
###################################################
def checkLicStatus(auth_token,ip,id):
  url = 'https://'+ip+'/mgmt/cm/device/tasks/licensing/pool/member-management/'+id
  headers = {
    'Content-Type': 'application/json',
    'X-F5-Auth-Token': auth_token
  }
  resp = requests.get(url,headers=headers, verify=False)
  json_data = json.loads(resp.text)

#GET_DEVICE
#LICENSE_ASSIGNMENT
#POLL_ASSIGNMENT_STATUS
#GET_CONFLICTING_ASSIGNMENTS

  currentStep = "STARTED"
  status = "STARTED"
  licenseText = ""

  while currentStep <> "FINISHED":
    resp = requests.get(url,headers=headers, verify=False) 
    json_data = json.loads(resp.text)
    currentStep = json_data['status']

    if currentStep == "FAILED":
      error = json_data['errorMessage']
      print("License assignment FAILED. Check that you are using unique values")
      print(error)
      licenseText = error
      currentStep = "FINISHED"
    print(currentStep)

#not licenseText:
#      licenseText = json_data['licenseText']
#
#  return licenseText
  return

args = vars(parser.parse_args())

if args['action'] == 'unreachable_license':
    biq_ip = args['bigiq_ip']
    biq_adm = args['bigiq_adm']
    biq_pwd = args['bigiq_pwd']
    bip_ip = args['bigip_ip']
    bip_mac = args['bigip_mac']
    use_mac = args['use_mac']
    tenant_desc = args['tenant_desc']
    pool = args['pool']
    hyper = args['hyper']
    sku1 = args['sku1']
    sku2 = args['sku2']
    auth_token = bigiq_authtoken(biq_ip,biq_adm,biq_pwd)
    unreachable_license(auth_token,biq_ip,bip_ip,bip_mac,use_mac,tenant_desc,hyper,sku1,sku2,pool)

if args['action'] == 'managed_license':
    biq_ip = args['bigiq_ip']
    biq_adm = args['bigiq_adm']
    biq_pwd = args['bigiq_pwd']
    bip_ip = args['bigip_ip']
    tenant_desc = args['tenant_desc']
    pool = args['pool']
    sku1 = args['sku1']
    sku2 = args['sku2']
    auth_token = bigiq_authtoken(biq_ip,biq_adm,biq_pwd)
    managed_license(auth_token,biq_ip,bip_ip,tenant_desc,sku1,sku2,pool)

if args['action'] == 'unmanaged_license':
    biq_ip = args['bigiq_ip']
    biq_adm = args['bigiq_adm']
    biq_pwd = args['bigiq_pwd']
    bip_ip = args['bigip_ip']
    bip_admin = args['bigip_ip']
    bip_user = args['bigip_user']
    bip_pass = args['bigip_pass']
    tenant_desc = args['tenant_desc']
    pool = args['pool']
    sku1 = args['sku1']
    sku2 = args['sku2']
    auth_token = bigiq_authtoken(biq_ip,biq_adm,biq_pwd)
    unmanaged_license(auth_token,biq_ip,bip_ip,bip_user,bip_pass,tenant_desc,sku1,sku2,pool)
