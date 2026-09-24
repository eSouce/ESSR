from gnuradio import gr, blocks, digital, filter
from gnuradio import dtv
import osmosdr

class dvbs2_tx(gr.top_block):
    def __init__(self, ts_file="payload.ts", samp_rate=4000000, center_freq=1450000000):
        gr.top_block.__init__(self, "DVB-S2 HackRF Transmitter")

        self.samp_rate = samp_rate
        self.center_freq = center_freq

        self.file_source = blocks.file_source(gr.sizeof_char*1, ts_file, True)
        self.stream_adaptor = dtv.dvbs2_stream_adaptor(dtv.FECFRAME_NORMAL, dtv.C1_2, dtv.RO_0_35, dtv.INPUT_TS)
        self.bbheader = dtv.dvbs2_bbheader(dtv.FECFRAME_NORMAL, dtv.C1_2, dtv.RO_0_35)
        self.fec = dtv.dvbs2_fec_encoder(dtv.FECFRAME_NORMAL, dtv.C1_2, dtv.RO_0_35)
        self.interleaver = dtv.dvbs2_interleaver(dtv.FECFRAME_NORMAL, dtv.C1_2, dtv.MOD_QPSK, dtv.RO_0_35)
        self.modulator = dtv.dvbs2_modulator(dtv.FECFRAME_NORMAL, dtv.C1_2, dtv.MOD_QPSK, dtv.RO_0_35)
        self.pl_framer = dtv.dvbs2_physical_ccm(dtv.FECFRAME_NORMAL, dtv.C1_2, dtv.MOD_QPSK, dtv.RO_0_35, dtv.PILOT_OFF)
        self.rrc_filter = filter.interp_fir_filter_ccf(2, filter.firdes.root_raised_cosine(1.0, samp_rate, samp_rate/2, 0.35, 100))
        self.amp = blocks.multiply_const_vcc((0.5, ))
      
        self.osmo_sink = osmosdr.sink(args="numchan=" + str(1) + " " + "hackrf")
        self.osmo_sink.set_sample_rate(self.samp_rate)
        self.osmo_sink.set_center_freq(self.center_freq, 0)
        self.osmo_sink.set_freq_corr(0, 0)
        self.osmo_sink.set_gain(14, 0)
        self.osmo_sink.set_if_gain(20, 0)

        self.connect((self.file_source, 0), (self.stream_adaptor, 0))
        self.connect((self.stream_adaptor, 0), (self.bbheader, 0))
        self.connect((self.bbheader, 0), (self.fec, 0))
        self.connect((self.fec, 0), (self.interleaver, 0))
        self.connect((self.interleaver, 0), (self.modulator, 0))
        self.connect((self.modulator, 0), (self.pl_framer, 0))
        self.connect((self.pl_framer, 0), (self.rrc_filter, 0))
        self.connect((self.rrc_filter, 0), (self.amp, 0))
        self.connect((self.amp, 0), (self.osmo_sink, 0))
