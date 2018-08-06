from pathlib import Path
from shutil import rmtree, copy2, copystat
from itertools import count
import PIL.Image
from jinja2 import Environment, PackageLoader
import pkg_resources
from zipfile import ZipFile


def collect_images(directory):
    directory = Path(directory)
    globs = ('*.jpg', '*.JPG', '*.jpeg', '*.JPEG')
    images = []
    for glob in globs:
        for child in directory.glob(glob):
            images.append(child.relative_to(directory))

    return list(sorted(images))


def make_thumbnail(path):
    image = PIL.Image.open(path)
    image.thumbnail((256, 256))
    return image


def generate_gallery(path):
    jenv = Environment(loader=PackageLoader('lafayette', '.'))
    template_single = jenv.get_template('single.jinja.html')
    template_index = jenv.get_template('index.jinja.html')

    path = Path(path)
    output = path / 'web_public'
    if output.exists():
        rmtree(output)
    output.mkdir()
    thumb_output = output / 'thumbnails'
    thumb_output.mkdir()
    image_output = output / 'images'
    image_output.mkdir()

    images = collect_images(path)

    for image, i in zip(images, count()):
        prev = None
        nxt = None
        if i - 1 >= 1:
            prev = images[i - 1]
        if i + 1 < len(images):
            nxt = images[i + 1]

        thumbnail = make_thumbnail(path / image)
        thumb_path = thumb_output / image.with_suffix('.jpeg')
        thumbnail.save(thumb_path, progression=True, quality=91)

        copystat(path / image, thumb_path)
        copy2(path / image, image_output / image)

        html_path = output / image.with_suffix('.html')

        with open(html_path, 'w') as f:
            context = {}
            for name in ('prev', 'nxt'):
                value = locals().get(name, None)
                if value:
                    context[name] = {
                        'thumb':
                        Path('thumbnails') / value.with_suffix('.jpeg'),
                        'link': value.with_suffix('.html')
                    }
            context['image'] = Path('images') / image

            f.write(template_single.render(context))

        copy2(
            pkg_resources.resource_filename('lafayette', 'styles.css'),
            output / 'styles.css')

    with ZipFile(output / 'images.zip', 'w') as z:
        for image in images:
            z.write(path/image, image)

    with open(output / 'index.html', 'w') as f:
        context = dict(images=map(lambda i: dict(link=i.with_suffix('.html'), thumb=Path('thumbnails') / i.with_suffix('.jpeg')), images))
        f.write(template_index.render(context))
