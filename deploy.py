import json
import boto3
import os
import fileinput
import re
import base64
import hashlib
import mimetypes
import wget
import uuid
import string
import zipfile
import sys
import markdown
import shutil
import io
import nbformat
from nbconvert import HTMLExporter
import hashlib
import datetime
import bs4 as soup
import rpy2.robjects as robjects

def unzip(source_filename, dest_dir):
    zf = zipfile.ZipFile(source_filename)
    zf.extractall(dest)

def get_filename(repo, branch):
    filename = repo[repo.rfind('/')+1:] + '-' + branch + '.zip'
    return filename

def download(repo, branch, dest, filename):
    src = repo + '/archive/' + branch +'.zip'
    if not(os.path.isdir(dest)):
        os.mkdir(dest)
    fname = wget.download(src)
    os.rename(fname, filename)

def get_src_dict(repo_root, parent, parsers):
    d = {}
    suffixes = parsers.keys()
    rootdir = repo_root.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        for file in files:
            i = file.rfind('.')
            if i != -1:
                ext = file[i:]
                if ext in suffixes:
                    d[path + '/' + file] = True
    return d

def get_content_dict(table):
    response = table.scan()
    items = response['Items']
    d = {}
    for item in items:
        uri = item['uri']
        d[uri] = item
    return d

def new_content_render_plan(repo_root, bucket, src_dict, content_dict, parsers, ignore):
    plan = []
    s = len(repo_root)
    srcs = src_dict.keys()
    oldHash = None
    for src in srcs:
        uri = src[s:]
        uri = bucket + uri
        if not(uri in ignore):
            isNew = True
            if uri in content_dict:
                isNew = False
                oldHash = content_dict[uri]['c_hash']
            ext = uri[uri.rfind('.'):]
            parser = parsers[ext]
            fname = os.path.basename(src)
            path = src[0:len(src) - len(fname)]
            p = fname.rfind('.')
            d = path + "src-" + fname[0:p]
            srcfiles = []
            if os.path.isdir(d):
                srcfiles = os.listdir(d)
            plan.append({"absfile": src, "srcfiles": srcfiles, "uri": uri, "parser": parser, "isNew": isNew, "oldHash": oldHash})
    return plan

def get_title(absfilename, contents):
    lcontents = contents.lower()
    c = 1
    b = soup.BeautifulSoup(contents, "lxml")
    while c < 6:
        tag = b.find('h' + str(c))
        if tag != None:
            return tag.text.replace('&#182;', '')
        c += 1
    i = absfilename.rfind('/')
    j = absfilename.rfind('.')
    fname = absfilename[i+1:j]
    fname = fname.replace('-', ' ').replace('_', ' ')
    fname = fname.title()
    return fname

def get_pretty_name(absfilename, title):
    i = absfilename.rfind('/')
    if absfilename[i+1:].lower() == 'readme.htm':
        return '/' + absfilename[0:i+1]
    pn = title.lower().replace(' ', '-')
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    pn2 = ''.join(c for c in pn if c in valid_chars)
    i = absfilename.rfind('/')
    return '/' + absfilename[0:i] + '/' + pn2

def get_desc(contents):
    lcontents = contents.lower()
    i = lcontents.find('<p>')
    if i != -1:
        j = lcontents.find('</p>', i)
        desc = contents[i+3:j-4]
        desc = re.sub('<[^<]+?>', '', desc)
        if desc != '':
            return desc
    return 'desc'

def next_delimiter(s, a, delim='$'):
    i = s.find(delim, a)
    if i == -1:
        return -1
    if i > 0:
        before = s[i-1]
        if before == '\\':
            return next_delimiter(s, a+1)
    return i

def render_uri(s3, bucket, absfile, parser):
    buck = s3.Bucket(bucket)
    rendered_map = {}
    contents = parser(absfile)
    if type(contents) != str:
        contents = contents.encode('utf-8')
    title = get_title(absfile, contents)
    desc = get_desc(contents)
    i = 0
    ranges = []
    while i < len(contents):
        i = next_delimiter(contents, i)
        if i != -1:
            j = next_delimiter(contents, i+1)
            if j != -1:
                ranges.append([i, j+1])
        if i == -1 or j == -1:
            i = len(contents)
        else:
            i = j + 1
    i = len(ranges) - 1
    # Go backwards because this is destructive of the source
    # Backwards makes debugging easier
    while i >= 0:
        r = ranges[i]
        b = r[0]
        e = r[1]
        latex = contents[b+1:e-1]
        #print("latex:", latex)
        # TODO: revisit and fix encoding
        aa = '&amp;'
        bb = '&'
        if type(latex) != str:
            latex = latex.decode('utf-8')
        latex = latex.replace(aa, bb)
        #latex = latex.replace('\\', '')
        fname = latex + ".svg"
        fname = fname.replace('\\', '_')
        fname = fname.replace(' ', '_')
        fname = fname.replace('=', '_')
        s3key = "latex/" + fname
        objs = list(buck.objects.filter(Prefix=s3key))
        if len(objs) > 0:
            rendered_map[s3key] = True
        #
        svguri = "http://s3.amazonaws.com/" + bucket + "/latex/" + fname
        if s3key in rendered_map:
            pass
        else:
            cmd = '/usr/local/lib/node_modules/mathjax-node/bin/tex2svg '
            cmd += '"' + latex + '"'
            rendered = os.popen(cmd).read()
            # TODO: use prettier filenames
            #fname = hashlib.sha224(rendered.encode('utf-8')).hexdigest() + ".svg"
            print(cmd)
            f = open(fname, 'w')
            f.write(rendered)
            f.close()
            # TODO: Check if it already exists since has is unique
            #fake_handle = StringIO(rendered)
            f = open(fname, 'rb')
            fake_handle = f
            print(svguri)
            fname = fname.encode('utf-8')
            res = buck.put_object(Key=s3key, Body=fake_handle, ContentType='image/svg+xml')
            os.remove(fname)
            rendered_map[s3key] = True
        imgTag = "<img className='latex-svg' src='" + svguri + "' alt='" + latex + "' />"
        if type(contents) != str:
            contents = contents.decode('utf-8')
        contents = contents[0:b] + imgTag + contents[e:len(contents)]
        i -= 1
    #
    return contents


def execute_plan(plan, s3, bucket, table, env):
    summary = []
    now = datetime.datetime.now()
    n = now.strftime('%Y-%m-%d')
    if env != 'dev':
        tomorrow = now + datetime.timedelta(days=1)
    else:
        tomorrow = now
    publish_date = tomorrow.strftime('%Y-%m-%d')
    for item in plan:
        parser = item['parser']
        absfile = item['absfile']
        uri = item['uri']
        f = open(absfile, 'rb')
        c = f.read()
        f.close()
        #m = hashlib.md5()
        #m.update(c)
        #hash = m.hexdigest()
        hash = hashlib.md5(c).hexdigest()
        #print("hash", hash)
        render = True
        if not(item['isNew']):
            if item['oldHash'] == hash:
                render = False
            else:
                render = True
        if render:
            contents = render_uri(s3, bucket, absfile, parser)
            title = get_title(absfile, contents)
            desc = get_desc(contents)
            fake_handle = io.BytesIO(contents.encode('utf-8'))
            a = len(bucket)+1
            i = uri.rfind('.')
            ext = uri[i:]
            s3key = uri[a:i] + '.htm'
            if s3key[0]=='/':
                s3key = s3key[1:]
            print('Deploying to: ' + bucket + '/' + s3key)
            prettyname = get_pretty_name(s3key, title)
            print(type(s3key))
            print(bucket)
            res = s3.Bucket(bucket).put_object(Key=s3key, Body=fake_handle)
            author = 'Kyle'
            ritem = {
                        'uri': uri,
                        'ext': ext,
                        'last_rendered': n,
                        'c_hash': hash,
                        'date_discovered': n,
                        'env': env,
                        'author': author,
                        'desc': desc,
                        'prettyname': prettyname,
                        'publish_date': publish_date,
                        'rendered': s3key,
                        'title': title
                    }
            print(ritem)
            x = os.path.basename(s3key)
            a = s3key.rfind('/')
            b = s3key.rfind('.')
            dname = 'src-' + s3key[a+1:b]
            keypath = s3key[0:len(s3key)-len(x)] + dname + '/'
            for src in item['srcfiles']:
                s3key2 = keypath + src
                print('Deploying source file: ' + s3key2)
                i = absfile.rfind('/')
                abspath = absfile[0:i]
                fp = open(abspath + '/' + dname + '/' + src, 'rb')
                data = fp.read()
                fp.close()
                res = s3.Bucket(bucket).put_object(Key=s3key2, Body=data)
            if item['isNew']:
                response = table.put_item(
                    Item=ritem
                )
            else:
                response = table.update_item(
                    Key={
                        'uri': uri
                    },
                    UpdateExpression="set last_rendered = :n, c_hash=:h",
                    ExpressionAttributeValues={
                        ':n': n,
                        ':h': hash
                    },
                    ReturnValues="UPDATED_NEW"
                )
            summary.append({"uri": uri})
    return summary

def send_summary(ses, summary, branch, bucket, recipients, efrom):
    response = ses.send_email(
        Source='kyle@dataskeptic.com',
        Destination={'ToAddresses': recipients},
        Message={
            'Subject': {
                'Data': 'Deploying ' + branch + ' to ' + bucket
            },
            'Body': {
                'Text': {
                    'Data': json.dumps(summary)
                }
            }
        },
        ReplyToAddresses=efrom
    )

def clean_up(dest):
    shutil.rmtree(dest)

def md(absfile):
    f = open(absfile, 'r')
    c = f.read()
    f.close()
    if type(c) == str:
        c = c.replace('\xe2\x80\x9c', '"')
        c = c.replace('\xe2\x80\x99', "'")
        c = c.replace('\xe2\x80\x9d', '"')
        c = c.replace('\xe2\x80\x93', "-")
        c = c.replace('\xe2\x80\x98', "'")
        c = c.replace('\xe2\x80\x94', "-")
        
        c = c.replace('\x91', '`')
        c = c.replace('\x92', '\'')
        c = c.replace('\x93', '"')
        c = c.replace('\x94', '"')
        c = c.replace('\x96', '-')
        c = c.replace('\x97', '-')
        #c = c.encode('utf-8')
    html = markdown.markdown(c, extensions=['markdown.extensions.tables'])
    return html

def replacement(match):
    fn = match.groups()[0]
    if os.path.isfile(fn):
        return 'src="data:%s;base64,%s"' % (mimetypes.guess_type(fn)[0], base64.b64encode(open(fn, 'rb').read()))
    return match.group()

def html_inline(s):
    fi = fileinput.FileInput(openhook=fileinput.hook_encoded("utf8"))
    return re.sub(r'src="(.*?)"', replacement, s).encode('utf-8')

def knitr(absfile):
    i = absfile.rindex('/')
    j = absfile.find('.', i)
    s = absfile[0:j]
    figpath = s + '_img/'
    r = robjects.r("""
        knitr::opts_chunk$set(echo=FALSE, fig.path='{}')
        library('knitr')
        knit('{}')
        """.format(figpath, absfile))
    fname = r[0]
    f = open(fname, 'r')
    c = f.read()
    f.close()
    if type(c) == str:
        c = unicode(c, 'utf-8')
    c2 = html_inline(c)
    os.remove(fname)
    # TODO: remove directory also
    return c2

def nbconvert(absfile):
    f = open(absfile, 'r')
    c = f.read()
    f.close()
    nb = nbformat.reads(c, as_version=4)
    html_exporter = HTMLExporter()
    html_exporter.template_file = 'basic'
    (body, resources) = html_exporter.from_notebook_node(nb)
    return body

if __name__ == "__main__":
    repo = 'https://github.com/data-skeptic/blog'
    tblName = 'blog'
    emails = ['kylepolich@gmail.com']
    ignore = ['/README.md']
    clean = True
    for item in sys.argv:
        if item == '--noclean':
            clean = False
            print("No cleaning")
    #
    parsers = {
        '.md': md,
        '.Rhtml': knitr,
        '.ipynb': nbconvert
    }
    #
    accessKey = os.environ['accessKey']
    secretKey = os.environ['secretKey']
    region = os.environ['region']
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=accessKey, aws_secret_access_key=secretKey, region_name=region)
    table = dynamodb.Table(tblName)
    s3 = boto3.resource('s3', aws_access_key_id=accessKey, aws_secret_access_key=secretKey, region_name=region)
    #ses = boto3.client('ses', aws_access_key_id=accessKey, aws_secret_access_key=secretKey, region_name=region)
    #
    environments = [
        {'branch': 'dev', 'bucket': 'dev.dataskeptic.com'}
        ,{'branch': 'master', 'bucket': 'dataskeptic.com'}
    ]
    #
    for env in environments:
        branch = env['branch']
        bucket = env['bucket']
        print("Running for " + branch)
        dest = '/tmp/' + str(uuid.uuid1()) + '/'
        os.makedirs(dest)
        filename = get_filename(repo, branch)
        if not(os.path.exists(filename)):
            print("Didn't find " + filename)
            download(repo, branch, dest, filename)
        x = unzip(filename, dest)
        if clean:
            os.remove(filename)
        # TODO: Check that no router paths match blog folders, /blog approx match goes to /blog/ml/2016/blah
        repo_root = dest + 'blog-' + branch
        src_dict = get_src_dict(repo_root, filename, parsers)
        content_dict = get_content_dict(table)
        plan = new_content_render_plan(repo_root, bucket, src_dict, content_dict, parsers, ignore)
        summary = execute_plan(plan, s3, bucket, table, branch)
        #if len(summary) > 0:
        #    send_summary(ses, summary, branch, bucket, emails, ['kyle@dataskeptic.com'])
        if clean:
            if os.path.exists(filename):
                os.remove(filename)
            clean_up(dest)




