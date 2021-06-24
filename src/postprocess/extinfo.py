import pandas as pd

from ..sequtils.orflib import ORF, ORFCollection


class ExtendedInformation(object):
    def __init__(self, folder, filetype, alternatives):
        """
        Adds spectrum information for each of the extended ORFs based on the peptides that match them.
        :param folder: either Genome or Transcriptome
        :param filetype: either genome or transcriptome
        :param alternatives: the dictionary containing ORFCollection() instances generated with AltCodons() class
        methods
        """
        self.folder = folder
        self.filetype = filetype
        self.alternatives = alternatives
        self.results = pd.read_csv(f'{self.folder}/post_perc/{self.filetype}_results_02.txt', sep='\t')
        self.peptides = self.__fix_peptides()

    def filter_alternatives(self, priorities):
        """
        Excludes all but the top priority START codon based on the list of priorities.
        :param priorities: list containing ORF names. Generated with get_priorities() method from AltCodons().
        :return:
        """
        alternatives = {}
        for stop in self.alternatives:
            i = 0
            for alt in self.alternatives[stop]:
                # if alt.name in priorities:
                if i == 0:
                    alternatives[stop] = ORFCollection()
                    alternatives[stop].add_orf(alt)
                    i += 1
        for stop in alternatives:
            for alt in alternatives[stop]:
                print(alt.name)
        self.alternatives = alternatives

    def __fix_peptides(self):
        peptides = self.results["Peptide"].tolist()

        def format_pep(pep):
            fixed = ""
            for i in pep:
                if i.isalpha():
                    fixed += i
            return fixed

        fixed_peptides = []
        for peptide in peptides:
            fixed = format_pep(peptide)
            fixed_peptides.append(fixed)
        self.results.insert(5, "Fixed Peptides", fixed_peptides)
        return fixed_peptides

    def extract_spectra(self):
        new_df = pd.DataFrame(columns=self.results.columns)
        # new_df.insert(3, "Extended ORF", [])
        extended = []
        ext_seqs = []
        dfdf = self.results.drop_duplicates(subset=["SpecFile", "ScanNum"], keep='last')
        # chunk_size = 10**6
        for stop in self.alternatives:
            # df = dfdf[dfdf["Genome Coordinates"].str.contains(str(stop))]
            new_stop = stop.split("_")
            if len(new_stop) > 1:
                real_stop = new_stop[1]
            else:
                real_stop = stop
            df = dfdf[dfdf["Protein"].str.contains(str(real_stop))]
            # df = df.drop_duplicates(subset=["SpecFile", "ScanNum"], keep='last')
            fixed_pep = df["Fixed Peptides"].tolist()
            for alt in self.alternatives[stop]:
                # print(alt.name)
                for pep in fixed_pep:
                    # print(pep)
                    # df = self.results[self.results["Fixed Peptides"].isin(alt.proteinSequence)]
                    ndf = df[df["db entry"].str.contains(pep)]
                    peps = ndf["Fixed Peptides"].tolist()
                    # extended = [alt.name for pep in peps]
                    for pep in peps:
                        extended.append(alt.name)
                        ext_seqs.append(alt.proteinSequence)
                    # if i == 0:
                    # ndf.insert(3, "Extended ORF", extended)
                    # i += 1
                    new_df = new_df.append(ndf)
        new_df.insert(3, "Extended ORF", extended)
        new_df.insert(4, "Extended Sequence", ext_seqs)

        new_df.to_csv(f'{self.folder}/post_perc/{self.filetype}_results_04.txt', sep='\t', index=False)
        return self




