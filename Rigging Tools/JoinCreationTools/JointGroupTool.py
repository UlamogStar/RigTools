import re
import maya.cmds as cmds

# Qt imports for Maya 2026: prefer PySide6, fallback to PySide2
try:
	from PySide6 import QtWidgets, QtCore
	import shiboken6 as shiboken
except Exception:
	try:
		from PySide2 import QtWidgets, QtCore
		import shiboken2 as shiboken
	except Exception:
		QtWidgets = None
		QtCore = None
		shiboken = None



def _group_key_from_name(name):
	# Derive a grouping base from the transform short name.
	# Strategy:
	#  - split the short name into tokens
	#  - remove numeric tokens and common suffix tokens
	#  - keep tokens that identify fingers (Indx, Pnky, Thmb, Pntr, Mdl)
	short = name.split('|')[-1]
	parts = re.split(r'[^A-Za-z0-9]+', short)
	remove = set(['jnt', 'fk', 'ik', 'handle', 'cluster', 'h', 'ctl', 'ctrl', 'clav'])
	out_parts = []
	for p in parts:
		if not p:
			continue
		if p.isdigit():
			continue
		low = p.lower()
		if low in remove:
			continue
		out_parts.append(p)

	base = '_'.join(out_parts)
	return base or short


def _extract_index(name):
	m = re.search(r'(\d+)$', name)
	return int(m.group(1)) if m else None


def _get_all_cluster_handle_transforms():
	"""Return a list of transforms that contain a clusterHandle shape."""
	shapes = cmds.ls(type='clusterHandle') or []
	transforms = []
	for sh in shapes:
		parents = cmds.listRelatives(sh, parent=True, fullPath=True) or []
		transforms.extend(parents)
	seen = set()
	out = []
	for t in transforms:
		if t not in seen:
			seen.add(t)
			out.append(t)
	return out


def _find_matching_cluster_transform(target_name, base, idx, cluster_transforms):
	"""Find best matching cluster transform from `cluster_transforms`.

	Priority:
	  1. exact short-name or full-name match
	  2. base + optional separator + index (exact)
	  3. startswith base with separator
	"""
	def short(n):
		return n.split('|')[-1]

	tgt_short = short(target_name)
	candidates = [(t, short(t)) for t in cluster_transforms]

	# 1) exact match
	for t, s in candidates:
		if s == tgt_short or t == target_name:
			return t

	# 2) index-based match (base + optional separator + index)
	if idx is not None and base:
		idx_str = str(idx)
		pat = re.compile(r'^' + re.escape(base) + r'[_-]?' + re.escape(idx_str) + r'$', flags=re.IGNORECASE)
		for t, s in candidates:
			if pat.match(s):
				return t

		for t, s in candidates:
			if s.lower().endswith(idx_str.lower()) and s.lower().startswith(base.lower()):
				return t

	# 3) base-only matches (exact or with separator)
	if base:
		for t, s in candidates:
			if s.lower() == base.lower():
				return t
		for t, s in candidates:
			if s.lower().startswith(base.lower() + '_') or s.lower().startswith(base.lower() + '-'):
				return t

	return None


def create_joints_from_selection(top_group_name='joints_from_clusters_grp'):
	"""Create joints at selected cluster handles and parent into chains.

	Returns a list of created root joints.
	"""
	if cmds is None:
		raise RuntimeError('This script must be run inside Maya where maya.cmds is available')

	sel = cmds.ls(selection=True) or []
	if not sel:
		cmds.warning('Select cluster handle transforms to create joints.')
		return []

	# Filter selection: prefer objects that have a clusterHandle shape under them,
	# but fall back to the raw selection if none detected.
	handles = []
	for s in sel:
		shapes = cmds.listRelatives(s, shapes=True, fullPath=True) or []
		if any(cmds.nodeType(sh).lower() == 'clusterHandle'.lower() for sh in shapes):
			handles.append(s)

	if not handles:
		handles = sel

	# Group handles by derived base name
	groups = {}
	for h in handles:
		base = _group_key_from_name(h)
		idx = _extract_index(h)
		groups.setdefault(base, []).append((h, idx))

	created_roots = []

	# Create a top group to hold all chains (avoid recreating if exists)
	if cmds.objExists(top_group_name):
		top_grp = top_group_name
	else:
		top_grp = cmds.group(empty=True, name=top_group_name)

	for base, items in groups.items():
		# sort by numeric suffix when available, otherwise by name
		items.sort(key=lambda x: (x[1] if x[1] is not None else float('inf'), x[0]))

		# create a group per chain
		safe_base = re.sub(r'[^0-9A-Za-z_]', '_', base) or 'chain'
		chain_grp = cmds.group(empty=True, name='{}_jnt_grp'.format(safe_base))
		cmds.parent(chain_grp, top_grp)

		prev_root = None
		prev_jnt = None
		# Prefer clav items first so clav becomes the chain parent
		def short(n):
			return n.split('|')[-1]

		clav_items = [it for it in items if 'clav' in short(it[0]).lower()]
		other_items = [it for it in items if 'clav' not in short(it[0]).lower()]
		other_items.sort(key=lambda x: (x[1] if x[1] is not None else float('inf'), x[0]))
		ordered = clav_items + other_items

		for i, (h, idx) in enumerate(ordered):
			# match an actual cluster transform in the scene when possible
			cluster_transforms = _get_all_cluster_handle_transforms()
			match = _find_matching_cluster_transform(h, base, idx, cluster_transforms)
			if match:
				pos = cmds.xform(match, q=True, ws=True, t=True)
				short_name = match.split('|')[-1]
			else:
				pos = cmds.xform(h, q=True, ws=True, t=True)
				short_name = short(h)
			# name joints based on base; ensure unique names by appending index
			if 'clav' in short_name.lower():
				# Create clav joint as root for the chain (no numeric suffix)
				jname = '{}_clav_jnt'.format(safe_base)
				j = cmds.joint(p=pos, name=jname)
				prev_root = j
				prev_jnt = j
			else:
				# create indexed FK/chain joints
				jname = '{}_{:02d}_jnt'.format(safe_base, (i if clav_items else i + 1))
				if prev_jnt is None:
					j = cmds.joint(p=pos, name=jname)
					prev_root = j
					prev_jnt = j
				else:
					cmds.select(prev_jnt)
					j = cmds.joint(p=pos, name=jname)
					prev_jnt = j

		# parent the chain root under the chain group to keep the outliner tidy
		if prev_root:
			cmds.parent(prev_root, chain_grp)
			created_roots.append(prev_root)

		# clear selection so further operations are predictable
		cmds.select(clear=True)

	cmds.select(created_roots)
	return created_roots


def create_joints_from_selection_ui(*args, **kwargs):
	"""Wrapper for attaching to UI buttons that ignore args."""
	return create_joints_from_selection(**kwargs)


if __name__ == '__main__':
	# simple test call when running the script directly inside Maya
	try:
		roots = create_joints_from_selection()
		print('Created root joints:', roots)
	except Exception as e:
		print('JointGroupTool error:', e)


# --------------------------
# Qt UI
# --------------------------


def _get_maya_main_window():
	if QtWidgets is None or shiboken is None:
		return None
	try:
		import maya.OpenMayaUI as omui
		ptr = omui.MQtUtil.mainWindow()
		if ptr is None:
			return None
		# wrapInstance needs an integer pointer
		try:
			return shiboken.wrapInstance(int(ptr), QtWidgets.QWidget)
		except Exception:
			return shiboken.wrapInstance(long(ptr), QtWidgets.QWidget)
	except Exception:
		return None


class JointGroupToolUI(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super(JointGroupToolUI, self).__init__(parent)
		self.setWindowTitle('Joint Group Tool')
		self.setMinimumWidth(360)

		layout = QtWidgets.QVBoxLayout(self)
		layout.setContentsMargins(8, 8, 8, 8)

		intro = QtWidgets.QLabel('Create joints at selected cluster handles and group chains by name')
		layout.addWidget(intro)

		row = QtWidgets.QHBoxLayout()
		lbl = QtWidgets.QLabel('Top Group:')
		row.addWidget(lbl)
		self.top_group_edit = QtWidgets.QLineEdit('joints_from_clusters_grp')
		row.addWidget(self.top_group_edit)
		layout.addLayout(row)

		btn_layout = QtWidgets.QHBoxLayout()
		self.create_btn = QtWidgets.QPushButton('Create Chains')
		self.create_btn.clicked.connect(self.on_create)
		btn_layout.addWidget(self.create_btn)

		self.close_btn = QtWidgets.QPushButton('Close')
		self.close_btn.clicked.connect(self.close)
		btn_layout.addWidget(self.close_btn)
		layout.addLayout(btn_layout)

		self.status = QtWidgets.QLabel('')
		layout.addWidget(self.status)

	def on_create(self):
		top = self.top_group_edit.text().strip() or 'joints_from_clusters_grp'
		try:
			roots = create_joints_from_selection(top_group_name=top)
			self.status.setText('Created %d chain root(s).' % (len(roots)))
		except Exception as e:
			self.status.setText('Error: %s' % (e,))


_ui_instance = None


def show_ui():
	"""Show the Qt UI inside Maya. Returns the dialog instance."""
	if QtWidgets is None:
		raise RuntimeError('Qt bindings not available (PySide6/PySide2).')

	global _ui_instance
	try:
		if _ui_instance is not None:
			_ui_instance.close()
			_ui_instance.deleteLater()
	except Exception:
		pass

	parent = _get_maya_main_window()
	_ui_instance = JointGroupToolUI(parent=parent)
	_ui_instance.setAttribute(QtCore.Qt.WA_DeleteOnClose)
	_ui_instance.show()
	return _ui_instance


if __name__ == '__main__':
	try:
		show_ui()
	except Exception:
		pass

