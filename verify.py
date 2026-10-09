"""Reproduce and verify the captured evidence offline. Python 3.9+, Node 22+, macOS/Linux."""
import hashlib,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def run(args,cwd):subprocess.run(args,cwd=cwd,check=True)

def main():
    run([sys.executable,'scripts/replay-marker-evidence.py','--check'],ROOT)
    run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_*.py','-v'],ROOT)
    run([sys.executable,'scripts/replay-medication-evidence.py','--check'],ROOT)
    artifacts=['evidence.json','review.json','changes.json','config.js']
    before={name:hashlib.sha256((ROOT/'dist'/name).read_bytes()).hexdigest() for name in artifacts}
    run([sys.executable,'-m','unittest','discover','-s','tests','-v'],ROOT/'research')
    run([sys.executable,'scripts/reconcile.py'],ROOT/'research')
    run([sys.executable,'prepare.py'],ROOT)
    after={name:hashlib.sha256((ROOT/'dist'/name).read_bytes()).hexdigest() for name in artifacts}
    if before!=after:raise SystemExit('Reproduction changed packaged evidence. Review source changes before publishing.')
    run([sys.executable,'research/scripts/snapshots.py','replay','dist/evidence.json'],ROOT)
    run(['node','--test','tests/resource.test.mjs','tests/genetics.test.mjs','tests/findings-replay.test.mjs','tests/medication-context.test.mjs','tests/insights.test.mjs','tests/slco1b1.test.mjs','tests/import-recovery.test.mjs','tests/evidence-path.test.mjs','tests/dpyd.test.mjs','tests/readable-report.test.mjs'],ROOT)
    run(['node','--check','dist/app.js'],ROOT)
    print('Offline reproduction passed: research, resource and genetic-reader tests, and byte-identical evidence artifacts.')
if __name__=='__main__':main()
