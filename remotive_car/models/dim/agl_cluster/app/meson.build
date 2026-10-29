# SPDX-License-Identifier: Apache-2.0
#
# RemotiveCar instrument cluster, derived from the AGL cluster demo dashboard
# (apps/agl-cluster-demo-dashboard). Reads the vehicle buses directly over
# SocketCAN with decoders generated from the platform DBC files.

project(
  'remotivecar-cluster',
  ['c', 'cpp'],
  version : '1.0.0',
  license : 'Apache-2.0',
  meson_version : '>= 0.60.0',
  default_options :
    [
      'warning_level=1',
      'buildtype=debugoptimized',
      'c_std=c17',
      'cpp_std=c++17'
    ],
)

qt = import('qt6')
cpp = meson.get_compiler('cpp')

qt_dep = dependency('qt6', modules: ['Core', 'Gui', 'Qml', 'Quick'])
wayland_dep = dependency('wayland-client', version: '>= 1.20.0')
scanner = find_program('wayland-scanner')
python = find_program('python3')

# The AGL compositor integration needs the QPA native interface header
qpa_header = join_paths(qt_dep.version(), 'QtGui', 'qpa/qplatformnativeinterface.h')
if not cpp.has_header(qpa_header, dependencies : qt_dep)
  error('QtGui private header ' + qpa_header + ' not found (install qt6-base-private-dev)')
endif
cpp_args = ['-DQT_QPA_HEADER=<@0@>'.format(qpa_header)]

# agl-shell protocol, used when running under agl-compositor
agl_shell_xml = files('protocol/agl-shell.xml')
agl_shell_sources = [
  custom_target('agl-shell-client-header',
    input: agl_shell_xml, output: 'agl-shell-client-protocol.h',
    command: [scanner, 'client-header', '@INPUT@', '@OUTPUT@']),
  custom_target('agl-shell-protocol-code',
    input: agl_shell_xml, output: 'agl-shell-protocol.c',
    command: [scanner, 'private-code', '@INPUT@', '@OUTPUT@']),
]

# CAN frame decoders generated from the platform DBC files with cantools
dbc_dir = get_option('dbc_dir')
dbc_sources = []
foreach db : ['chassis_can', 'body_can']
  dbc_sources += custom_target(db,
    input: join_paths(dbc_dir, db + '.dbc'),
    output: [db + '.c', db + '.h'],
    command: [python, '-m', 'cantools', 'generate_c_source', '@INPUT@', '-o', '@OUTDIR@'])
endforeach

moc_files = qt.compile_moc(headers: ['cansignals.h'], dependencies: qt_dep)
resources = qt.compile_resources(sources: ['cluster.qrc'])

executable('cluster-dashboard',
  ['main.cpp', 'cansignals.cpp', agl_shell_sources, dbc_sources, moc_files, resources],
  cpp_args: cpp_args,
  dependencies: [qt_dep, wayland_dep],
  install: true)
