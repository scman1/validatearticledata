def htmlAddInfo(url):
    import socket
    ipInfo(socket.gethostbyname(url))


def ipInfo(addr=''):
    from urllib.request import urlopen
    from json import load
    if addr == '':
        url = 'https://ipinfo.io/json'
    else:
        url = 'https://ipinfo.io/' + addr + '/json'
    res = urlopen(url)
    #response from url(if res==None then check connection)
    data = load(res)
    #will load the json response into data
    for attr in data.keys():
        #will print the data line by line
        print(attr,' '*13+'\t->\t',data[attr])



repositories = ["researchdata.gla.ac.uk","www.ccdc.cam.ac.uk", "www.rsc.org","aac.asm.org",
"aiche.onlinelibrary.wiley.com", "aip.scitation.org", "ars.els-cdn.com", "chemistry-europe.onlinelibrary.wiley.com",
"data.bris.ac.uk", "data.isis.stfc.ac.uk", "edata.stfc.ac.uk", "eprints.soton.ac.uk",
"github.com", "onlinelibrary.wiley.com", "ora.ox.ac.uk", "pubs.acs.org",
"pubs.rsc.org", "pure.qub.ac.uk", "pureapps2.hw.ac.uk", "rcahdrive.rc-harwell.ac.uk"
"res.mdpi.com", "research.cardiff.ac.uk", "risweb.st-andrews.ac.uk", "rs.figshare.com"
"s3-eu-west-1.amazonaws.com", "science.sciencemag.org",
"static-content.springer.com", "www.beilstein-journals.org", "www.nature.com", "zivahub.uct.ac.za"]

for repo in repositories:
    print("***", repo)
    htmlAddInfo(repo)
