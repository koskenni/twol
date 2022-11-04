Upgrading twol package from Python 3.6 to 3.9
=============================================

1) Downloaded a recent twol-dev package which is said to be compatible with
   Python 3.9:
   
     hfst_dev-3.15.0.10b0-cp39-cp39-manylinux_2_5_x86_64.manylinux1_x86_64.whl
   
   from PyPI: https://pypi.org/project/hfst-dev/3.15.0.10b0/#files

2) Installed it locally:

   $ pip3 install --upgrade --user --force ~/tmp/hfst_dev-3.15.0.10b0-cp39-cp39-manylinux_2_5_x86_64.manylinux1_x86_64.whl

3) Installed a newer version of TatSu, i.e. 5.7 which is said to be compatible
   with Python 3.8 and up.  (The latest version goes with 3.10 and up):

     pip3 install --user TatSu==5.7

4) Located all "import hfst" (by egrep 'import .*hfst' *.py) and changed 
   them into "import hfst_dev as hfst".

5) Located all calls "HfstBasicTransducer()" and converted them into
   "HfstIterableTransducer()" as the newer HFST requires.

6) Corrected the syntax of twolcsyntax.ebnf so that it handles multiple context
   parts in twol rules.  (Removed also some constructs that do not belong
   to the twol algebra, e.g. ".u", ".l" and ".o.".) 

7) Github had removed the usercode+password authentication, so "git push"
   did'n work. So, I changed to SSH::
     $ git remote -v
     $ git remote set-url origin git@github.com:koskenni/twol.git
