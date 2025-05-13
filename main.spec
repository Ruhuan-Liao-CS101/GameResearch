# tetris_game.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['main.py'],  # Your entry point file
             pathex=[],
             binaries=[],
             datas=[
                # TetrisGame files
                ('TetrisGame/font/font.ttf', 'TetrisGame/font/'),
                ('TetrisGame/img/background2.webp', 'TetrisGame/img/'),
                ('TetrisGame/img/img1.webp', 'TetrisGame/img/'),
                ('TetrisGame/img/photo1.jpeg', 'TetrisGame/img/'),
                ('TetrisGame/main.py', 'TetrisGame/'),
                ('TetrisGame/tetris_game.py', 'TetrisGame/'),
                # scenes files
                ('scenes/avatars/', 'scenes/avatars/'),
                ('scenes/backgrounds/', 'scenes/backgrounds/'),
                ('scenes/avatars_data.json', 'scenes/')
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='TetrisGame',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False)
          
app = BUNDLE(exe,
         name='TetrisGame.app',
         icon=None,
         bundle_identifier=None) 