from tests.patches_data import GIT, RAW
    p = patch.FilePatchDiff('chrome/file.cc', RAW.PATCH, [])
    self._check_patch(p, 'chrome/file.cc', RAW.PATCH)
    p = patch.FilePatchDiff('git_cl/git-cl', GIT.MODE_EXE, [])
        p, 'git_cl/git-cl', GIT.MODE_EXE, is_git_diff=True, patchlevel=1,
    p = patch.FilePatchDiff('git_cl/git-cl', GIT.MODE_EXE_JUNK, [])
        p, 'git_cl/git-cl', GIT.MODE_EXE_JUNK, is_git_diff=True, patchlevel=1,
    p = patch.FilePatchDiff('foo', RAW.NEW, [])
    self._check_patch(p, 'foo', RAW.NEW, is_new=True)
    p = patch.FilePatchDiff('foo', GIT.NEW, [])
    self._check_patch(
        p, 'foo', GIT.NEW, is_new=True, is_git_diff=True, patchlevel=1)

  def testValidSvn(self):
    # pylint: disable=R0201
    # Method could be a function
    # Should not throw.
    p = patch.FilePatchDiff('chrome/file.cc', RAW.PATCH, [])
    lines = RAW.PATCH.splitlines(True)
    header = ''.join(lines[:4])
    hunks = ''.join(lines[4:])
    self.assertEquals(header, p.diff_header)
    self.assertEquals(hunks, p.diff_hunks)
    self.assertEquals(RAW.PATCH, p.get())

  def testValidSvnNew(self):
    p = patch.FilePatchDiff('chrome/file.cc', RAW.MINIMAL_NEW, [])
    self.assertEquals(RAW.MINIMAL_NEW, p.diff_header)
    self.assertEquals('', p.diff_hunks)
    self.assertEquals(RAW.MINIMAL_NEW, p.get())

  def testValidSvnDelete(self):
    p = patch.FilePatchDiff('chrome/file.cc', RAW.MINIMAL_DELETE, [])
    self.assertEquals(RAW.MINIMAL_DELETE, p.diff_header)
    self.assertEquals('', p.diff_hunks)
    self.assertEquals(RAW.MINIMAL_DELETE, p.get())

  def testRelPath(self):
    patches = patch.PatchSet([
        patch.FilePatchDiff('chrome/file.cc', RAW.PATCH, []),
        patch.FilePatchDiff(
            'tools\\clang_check/README.chromium', GIT.DELETE, []),
        patch.FilePatchDiff('tools/run_local_server.sh', GIT.RENAME, []),
        patch.FilePatchDiff(
            'chromeos\\views/webui_menu_widget.h', GIT.RENAME_PARTIAL, []),
        patch.FilePatchDiff('pp', GIT.COPY, []),
        patch.FilePatchDiff('foo', GIT.NEW, []),
        patch.FilePatchDelete('other/place/foo', True),
        patch.FilePatchBinary('bar', 'data', [], is_new=False),
    ])
    expected = [
        'chrome/file.cc', 'tools/clang_check/README.chromium',
        'tools/run_local_server.sh',
        'chromeos/views/webui_menu_widget.h', 'pp', 'foo',
        'other/place/foo', 'bar']
    self.assertEquals(expected, patches.filenames)
    orig_name = patches.patches[0].filename
    orig_source_name = patches.patches[0].source_filename or orig_name
    patches.set_relpath(os.path.join('a', 'bb'))
    expected = [os.path.join('a', 'bb', x) for x in expected]
    self.assertEquals(expected, patches.filenames)
    # Make sure each header is updated accordingly.
    header = []
    new_name = os.path.join('a', 'bb', orig_name)
    new_source_name = os.path.join('a', 'bb', orig_source_name)
    for line in RAW.PATCH.splitlines(True):
      if line.startswith('@@'):
        break
      if line[:3] == '---':
        line = line.replace(orig_source_name, new_source_name)
      if line[:3] == '+++':
        line = line.replace(orig_name, new_name)
      header.append(line)
    header = ''.join(header)
    self.assertEquals(header, patches.patches[0].diff_header)

  def testRelPathEmpty(self):
    patches = patch.PatchSet([
        patch.FilePatchDiff('chrome\\file.cc', RAW.PATCH, []),
        patch.FilePatchDelete('other\\place\\foo', True),
    ])
    patches.set_relpath('')
    self.assertEquals(
        ['chrome/file.cc', 'other/place/foo'],
        [f.filename for f in patches])
    self.assertEquals([None, None], [f.source_filename for f in patches])

  def testBackSlash(self):
    mangled_patch = RAW.PATCH.replace('chrome/', 'chrome\\')
    patches = patch.PatchSet([
        patch.FilePatchDiff('chrome\\file.cc', mangled_patch, []),
        patch.FilePatchDelete('other\\place\\foo', True),
    ])
    expected = ['chrome/file.cc', 'other/place/foo']
    self.assertEquals(expected, patches.filenames)
    self.assertEquals(RAW.PATCH, patches.patches[0].get())

  def testDelete(self):
    p = patch.FilePatchDiff('tools/clang_check/README.chromium', RAW.DELETE, [])
        p, 'tools/clang_check/README.chromium', RAW.DELETE, is_delete=True)

  def testGitDelete(self):
    p = patch.FilePatchDiff('tools/clang_check/README.chromium', GIT.DELETE, [])
    self._check_patch(
        p, 'tools/clang_check/README.chromium', GIT.DELETE, is_delete=True,
        is_git_diff=True, patchlevel=1)

  def testGitRename(self):
    p = patch.FilePatchDiff('tools/run_local_server.sh', GIT.RENAME, [])
    self._check_patch(p, 'tools/run_local_server.sh', GIT.RENAME,
        is_git_diff=True, patchlevel=1,
        source_filename='tools/run_local_server.PY', is_new=True)

  def testGitRenamePartial(self):
    p = patch.FilePatchDiff(
        'chromeos/views/webui_menu_widget.h', GIT.RENAME_PARTIAL, [])
    self._check_patch(
        p, 'chromeos/views/webui_menu_widget.h', GIT.RENAME_PARTIAL,
        source_filename='chromeos/views/DOMui_menu_widget.h', is_git_diff=True,
        patchlevel=1, is_new=True)

  def testGitCopy(self):
    p = patch.FilePatchDiff('pp', GIT.COPY, [])
    self._check_patch(p, 'pp', GIT.COPY, is_git_diff=True, patchlevel=1,
        source_filename='PRESUBMIT.py', is_new=True)

  def testOnlyHeader(self):
    p = patch.FilePatchDiff('file_a', RAW.MINIMAL, [])
    self._check_patch(p, 'file_a', RAW.MINIMAL)

  def testSmallest(self):
    p = patch.FilePatchDiff('file_a', RAW.NEW_NOT_NULL, [])
    self._check_patch(p, 'file_a', RAW.NEW_NOT_NULL)

  def testRenameOnlyHeader(self):
    p = patch.FilePatchDiff('file_b', RAW.MINIMAL_RENAME, [])
    self._check_patch(
        p, 'file_b', RAW.MINIMAL_RENAME, source_filename='file_a', is_new=True)

  def testGitCopyPartial(self):
    p = patch.FilePatchDiff('wtf2', GIT.COPY_PARTIAL, [])
    self._check_patch(
        p, 'wtf2', GIT.COPY_PARTIAL, source_filename='wtf', is_git_diff=True,
        patchlevel=1, is_new=True)

  def testGitNewExe(self):
    p = patch.FilePatchDiff('natsort_test.py', GIT.NEW_EXE, [])
    self._check_patch(
        p, 'natsort_test.py', GIT.NEW_EXE, is_new=True, is_git_diff=True,
        patchlevel=1, svn_properties=[('svn:executable', '*')])

  def testGitNewMode(self):
    p = patch.FilePatchDiff('natsort_test.py', GIT.NEW_MODE, [])
    self._check_patch(
        p, 'natsort_test.py', GIT.NEW_MODE, is_new=True, is_git_diff=True,
        patchlevel=1)


class PatchTestFail(unittest.TestCase):
  # All patches that should throw.
  def testFilePatchDelete(self):
    p = patch.FilePatchDelete('foo', False)
    try:
      p.get()
      self.fail()
    except NotImplementedError:
      pass

  def testFilePatchDeleteBin(self):
    p = patch.FilePatchDelete('foo', True)
    try:
      p.get()
      self.fail()
    except NotImplementedError:
      pass
      patch.FilePatchDiff('foo', RAW.PATCH, [])
        patch.FilePatchDiff('chrome\\file.cc', RAW.PATCH, []),