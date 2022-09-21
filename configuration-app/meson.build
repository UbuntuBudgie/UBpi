
project(
  'budgie-pi',
  meson_version: '>= 0.40.0',
  default_options: ['prefix=/usr', 'libdir=/usr/lib']
)

appdir = 'arm'

prefix = get_option('prefix')
libdir = join_paths(prefix, get_option('libdir'))
INSTALL_DIR = join_paths(libdir, 'budgie-desktop', appdir)

subdir('src')
subdir('data')
subdir('ui')

install_data(
    'schema/org.ubuntubudgie.armconfig.gschema.xml',
    install_dir: '/usr/share/glib-2.0/schemas',
)

meson.add_install_script('meson_post_install.py')
