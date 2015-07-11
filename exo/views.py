import StringIO
import binascii
import pprint

from PIL import Image

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse

from exo.models import PictureSimple, ContentKey
from eso.base32 import base32
from eso.base32 import randspace

import json

def random(request):
    """Given a / URL, return another URL encoded as /meta/abcdefghij which
returns a page containing an image url"""
    # If this is slow in production, use this tip instead;
    # http://stackoverflow.com/a/2118712/682915
    p=PictureSimple.objects.order_by('?')[0]
    base32md5=(base32.b32encode(binascii.unhexlify(p.file_hash)))
    return HttpResponseRedirect("%s" %
        (request.build_absolute_uri(reverse('exo.views.page_by_base32',args=[base32md5]))))

def page_by_contentkey(request, contentkey):
    try:
        zerothfile=ContentKey.objects.filter(key=contentkey)[0].contentsignature_set.all()[0].contentinstance_set.all()[0]
        filename = "/".join([zerothfile.content_container.path,zerothfile.relpath,zerothfile.filename])
    except:
        filename="File not found"
    return HttpResponse(filename, content_type="text/plain")

def page_by_base32(request, base32md5):
    """Return a page with an image link by base32md5 and a link back to / URL
for another load"""
    p=PictureSimple.objects.get(file_hash=binascii.hexlify(base32.b32decode(base32md5)))
    import eso.exif.EXIF
    f = open(p.get_local_path(), 'rb')
    exifhash = eso.exif.EXIF.process_file(f)

    for key in exifhash.keys():
        try:
            if len(str(exifhash[key])) > 50:
                del exifhash[key]
        except:
                del exifhash[key]
    exifdata = pprint.pformat(exifhash, indent=1, width=50, depth=1)
    template = loader.get_template("meta.html")
    context = RequestContext(request, {
        'description': p.filename,
        'destination': request.build_absolute_uri(reverse('exo.views.random')),
        'imagesource': request.build_absolute_uri(reverse('exo.views.image_by_base32',args=[base32md5])),
        'exifdata': exifdata })
    return HttpResponse(template.render(context))

def image_by_base32(request, base32md5):
    """Return a resized file by the base32md5"""
    p=PictureSimple.objects.get(file_hash=binascii.hexlify(base32.b32decode(base32md5)))
    return HttpResponse(
        image_it(p.get_local_path()),
        content_type="image/jpeg"
        )

def privacy_unchecked(request):
    batchsize=24
    unchecked=PictureSimple.objects.filter(private=None).order_by('directory','filename')
    remaining=unchecked.count()/batchsize
    pictures = unchecked[0:batchsize]
    allbutton = ",".join([x.b32md5 for x in pictures])
    template = loader.get_template("private.html")
    context = RequestContext(request, {'pictures': pictures, 'allbutton': allbutton, 'remaining':remaining})
    return HttpResponse(template.render(context))

def update_privacy(request, actiontext, md5list):
    """Take a comma delimited string of base32 md5 plus an action text of private or public
and iterate over the results to change the status of individual images"""
    if actiontext not in ['private','public','reset']:
        return HttpResponse("Invalid command")

    try:
        md5hexlist = [binascii.hexlify(base32.b32decode(md5)) for md5 in md5list.split(",")]
    except:
        return HttpResponse("Bad list of elements")

    privacy=None
    if actiontext=='private':
        privacy=1
    if actiontext=='public':
        privacy=0

    PictureSimple.objects.filter(file_hash__in=md5hexlist).update(private = privacy)

    return HttpResponseRedirect("/")

def image(request, image_id):
    p=Picture.objects.get(pk=image_id)
    return HttpResponse(
        image_it(p.directory+"/"+p.filename),
        content_type="image/jpeg"
        )

def thumbnail(request, image_id):
    p=Picture.objects.get(pk=image_id)
    return HttpResponse(
        thumbnail_it(p.directory+"/"+p.filename),
        content_type="image/jpeg"
        )

def randomold(request):
    match=0
    while 1:
        try:
            g=Random()
            p=Old_Picture.objects.get(pk=g.randint(1,Old_Picture.objects.count()))
            break
        except Old_Picture.DoesNotExist:
            pass
    return HttpResponse(
        thumbnail_it('/local/img/'+p.theme.directory+"/"+p.filename+'.jpg'),
        content_type="image/jpeg"
        )

def thumbnail_it(path_to_original):
    im = Image.open(path_to_original)
    size = 240,180
    im.thumbnail(size, Image.ANTIALIAS)
    buf= StringIO.StringIO()
    im.save(buf, format= 'JPEG')
    return buf.getvalue()

def image_it(path_to_original):
    im = Image.open(path_to_original)
    size = 1024,1024,180
    im.thumbnail(size, Image.ANTIALIAS)
    buf= StringIO.StringIO()
    im.save(buf, format= 'JPEG')
    return buf.getvalue()

def new_id(request):
    payload={'id': randspace.randid()}
    response=json.dumps(payload, indent=4)
    return HttpResponse(response, content_type="application/json")
