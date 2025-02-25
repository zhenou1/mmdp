#!/usr/bin/env python

import subprocess as _sp
import tempfile as _tf
import multiprocessing as _mp

from Bio import SeqIO as _sqio
import sys

_NEWLINE = """
"""

def set_global_lock(l):
	global lock
	lock = l

class NeedleAll():
	def __init__(self, outfile1, outfile2, gap_open_penalty=10, gap_extend_penalty=0.5, threshold=-1):
		self.outfile1 = outfile1
		self.outfile2 = outfile2
		self.gap_open_penalty = gap_open_penalty
		self.gap_extend_penalty = gap_extend_penalty
		self.record_id_map = {}
		self.threshold = threshold

	def run_record(self, record_id, seqfile):
		print(record_id)
		with _tf.NamedTemporaryFile(suffix='.fasta') as aseq, \
                     _tf.NamedTemporaryFile(suffix='.fasta') as bseq, \
		     _tf.NamedTemporaryFile('r', suffix='.needleout') as needleout:
			keep_entry = False

			for record in _sqio.parse(seqfile, 'fasta'):
				if record.id == record_id:
					aseq.write(record.format('fasta').encode())
					keep_entry = True

				if keep_entry:
					bseq.write(record.format('fasta').encode())

			aseq.seek(0)
			bseq.seek(0)

			# Generate the command and run needleall
			command = ['needleall',	'-asequence', aseq.name, '-bsequence', bseq.name,
				'-gapopen', f'{self.gap_open_penalty}', '-gapextend',f'{self.gap_extend_penalty}',
				'-outfile', needleout.name, '-aformat3', 'pair']

			process = _sp.Popen(command, stdout=_sp.PIPE, stderr=_sp.PIPE)
			stdout, stderr = process.communicate()
			# Parse the output file
			identities = []
			similarities = []
			with open(needleout.name, 'r') as f:
				id1, id2, identity, similarity = None, None, None, None
				for line in f:
					if line.strip().startswith('# 1:'):
						id1 = line.strip().split()[2]

					if line.strip().startswith('# 2:'):
						id2 = line.strip().split()[2]

					if line.strip().startswith('# Identity'):
						num1, den1 = line.strip().split()[2].split('/')
						num1, den1 = int(num1), int(den1)
						identity = num1 / den1
						identities.append((id1, id2, identity,))

					if line.strip().startswith('# Similarity'):
						num2, den2 = line.strip().split()[2].split('/')
						num2, den2 = int(num2), int(den2)
						similarity = num2 / den2
						similarities.append((id1, id2, similarity,))

						# Reset variables so that any future iterations don't use these.
						num1, den1, num2, den2, similarity, identity, id1, id2 = None, None, None, None, None, None, None, None


		with lock:
			with open(self.outfile1, 'a') as f1:
				for id1, id2, identity in identities:
					if not identity >= self.threshold:
						continue
					f1.write(f"{self.record_id_map[id1]} {self.record_id_map[id2]} {identity}{_NEWLINE}")
			
			with open(self.outfile2, 'a') as f2:
				for id1, id2, similarity in similarities:
					if not similarity >= self.threshold:
						continue
					f2.write(f"{self.record_id_map[id1]} {self.record_id_map[id2]} {similarity}{_NEWLINE}")


	def run(self, seqfile):
		jobs = []

		with _tf.NamedTemporaryFile() as f:
			counter = 0
			for record in _sqio.parse(seqfile, 'fasta'):
				new_id = f'R{counter}'
				self.record_id_map[new_id] = record.id
				record.id = new_id
				f.write(record.format('fasta').encode())
				f.seek(0,2)
				jobs.append( (record.id, f.name) )
				counter += 1


			lock = _mp.Lock()
			with _mp.Pool(_mp.cpu_count(), initializer=set_global_lock, initargs=(lock,)) as pool:
				pool.starmap(self.run_record, jobs, chunksize=1)


if __name__ == '__main__':
	A = NeedleAll("identities.txt", "similarities.txt")
	A.run(sys.argv[1])
