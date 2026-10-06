#!/bin/bash
# Instala o Godot 4.4.1 e os modelos de export (Web e Windows) num container novo.
set -e
V=4.4.1-stable
U=https://github.com/godotengine/godot/releases/download/$V
mkdir -p /opt/godot ~/.local/share/godot/export_templates
cd /tmp
curl -sSLO $U/Godot_v${V}_linux.x86_64.zip && unzip -o -q Godot_v${V}_linux.x86_64.zip
mv -f Godot_v${V}_linux.x86_64 /opt/godot/godot && chmod +x /opt/godot/godot
curl -sSLO $U/Godot_v${V}_export_templates.tpz && unzip -o -q Godot_v${V}_export_templates.tpz
rm -rf ~/.local/share/godot/export_templates/4.4.1.stable
mv templates ~/.local/share/godot/export_templates/4.4.1.stable
echo "godot ok: /opt/godot/godot (use GODOT=/opt/godot/godot bash tools/build_web.sh)"
