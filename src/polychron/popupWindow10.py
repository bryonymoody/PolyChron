import os
import pickle
import tkinter as tk

import networkx as nx
import numpy as np
import pandas as pd
from networkx.drawing.nx_pydot import write_dot

from . import globals
from .util import imgrender, imgrender2, phase_relabel


class popupWindow10(object):
      def __init__(self, master, path):
          self.master = master
          self.path = path
          # for i in range(20,140):
          #     katz_df_subset = katz_df_test.sort_values(by='pagerank', ascending = False).head(i)
        #   ref_wd = os.getcwd()
     #     con_list = list(katz_df_test['context'])
          base_cont_type =  self.master.CONT_TYPE
          base_key_ref = self.master.key_ref
          base_context_no = self.master.CONTEXT_NO
          base_graph = self.master.graph
          base_chrono_graph = self.master.chrono_dag
          base_phi_ref = self.master.phi_ref
          base_prev_phase = self.master.prev_phase
          base_post_phase = self.master.post_phase
          base_context_no_unordered = self.master.context_no_unordered
          
          
          for num in range(5,6):
          #for loop would start here
              os.chdir(path)
              self.master.CONT_TYPE = base_cont_type.copy()
              self.master.key_ref = base_key_ref.copy()
              self.master.CONTEXT_NO = base_context_no.copy()
              self.master.graph = base_graph.copy()
              self.master.chrono_dag = base_chrono_graph.copy()
              self.master.phi_ref = base_phi_ref.copy()
              self.master.prev_phase = base_prev_phase.copy()
              self.master.post_phase = base_post_phase.copy()    
              self.master.context_no_unordered = base_context_no_unordered.copy()
              katz_df_test = self.top_nodes(num, self.master.phi_ref, self.master.CONTEXT_NO, self.master.key_ref, path)
              #remove_node_section
              remove_conts = [i for i in self.master.CONTEXT_NO if i not in katz_df_test]
              print('remove contexts')
          
              print(len(remove_conts))
              for j in remove_conts:
                  self.master.chrono_dag.remove_node(j)     
                  self.master.graph.remove_node(j)   
                  ref = np.where(np.array(self.master.CONTEXT_NO) == str(j))[0][0]
                  ref2 = np.where(np.array(self.master.context_no_unordered) == str(j))[0][0]
                  phase = self.master.key_ref[ref]              
                  phase_ref = np.where(np.array(base_phi_ref) == str(phase))[0][0]
                  self.master.CONT_TYPE.pop(ref)
                  self.master.key_ref.pop(ref)
                  self.master.CONTEXT_NO.pop(ref)   
                  self.master.context_no_unordered.pop(ref2)
        ## ###correcting phases for removed nodes
        #change to new phase rels
                  self.graph_adjust(phase, phase_ref)
                  ######## sorting floating nodes
                  group_conts = [self.master.CONTEXT_NO[i] for i,j in enumerate(self.master.key_ref) if j == phase]
                  for m in group_conts:
                      if len(self.master.chrono_dag.out_edges(m)) == 0:
                         alph = [i for i in self.master.chrono_dag.nodes() if "a_" + phase in i]
                         self.master.chrono_dag.add_edge(m, alph[0], arrowhead = 'none')
                      if len(self.master.chrono_dag.in_edges(m)) == 0:
                          bet = [i for i in self.master.chrono_dag.nodes() if "b_" + phase in i]
                          self.master.chrono_dag.add_edge(bet[0], m, arrowhead = 'none')
        #############################    setting up the directorys
              dirs4 = self.make_directories('testing' + str(num))
              write_dot(self.master.chrono_dag, 'fi_new_chrono')
              imgrender2(self.master.littlecanvas2.winfo_width(), self.master.littlecanvas2.winfo_height())  
              imgrender(self.master.graph, self.master.littlecanvas.winfo_width(), self.master.littlecanvas.winfo_height())
              self.master.ACCEPT = [[]]
              while min([len(i) for i in self.master.ACCEPT]) < 50000:
                       self.master.CONTEXT_NO, self.master.ACCEPT, self.master.PHI_ACCEPT, self.master.PHI_REF, self.master.A, self.master.P, self.master.ALL_SAMPS_CONT, self.master.ALL_SAMPS_PHI, self.master.resultsdict, self.master.all_results_dict = self.master.MCMC_func()
              globals.mcmc_check = 'mcmc_loaded'
              self.save_state_1(self.master, dirs4)
              
      def katz_plus_overlap(self, path, refmodel, mode = 'strat'): 
          if mode == 'strat':
              katz_df_test = pd.read_csv(path + "/" + refmodel + "/katz_centr_strat.csv") # katz centrality worked out for the reference model
          elif mode == 'chrono':
              katz_df_test = pd.read_csv(path + "/" + refmodel + "/katz_centr_chrono.csv") 
          katz_df_test = katz_df_test[['context', 'pagerank']]
          katz_df_test['context'] = katz_df_test['context'].astype(str)
          katz_df_test = katz_df_test.loc[(not katz_df_test["context"].str.contains("a"))]
          katz_df_test = katz_df_test.loc[(not katz_df_test["context"].str.contains("b"))]
          katz_df_test = katz_df_test.transpose()
          katz_df = katz_df_test.rename(columns=katz_df_test.iloc[0]).drop(katz_df_test.index[0]).reset_index(drop=True)    
          ll_over_df = pd.read_csv(path + "/" + refmodel + "/overlap_df.csv")
          ll_over_df = pd.DataFrame(ll_over_df[['node', 'neighbour', 'overlap_measure']]) #overlap df for the reference model
          ll_over_df['neighbour'] = ll_over_df['neighbour'].astype(str)
          ll_over_df['node'] = ll_over_df['node'].astype(str)
          return katz_df, ll_over_df             
              
      def katz_w_weight(self, path):
         with open(path + "/reference_model/python_only/save.pickle", "rb") as f:
             data = pickle.load(f)   
         ref_graph = data['graph'] 
         katz_df, ll_over_df =  self.katz_plus_overlap(path, 'reference_model', mode = 'chrono')  
         ll_over_df['neighbour'] = ll_over_df['neighbour'].astype(str)
         ll_over_df['node'] = ll_over_df['node'].astype(str)
         for v, w in ref_graph.edges: 
             ref_graph.edges[v, w]["weight"] = float(ll_over_df.loc[(ll_over_df['node'] == v) & (ll_over_df['neighbour'] == w)]['overlap_measure'])
         weighted_katz = nx.pagerank(ref_graph.to_undirected())  
         return weighted_katz
              
              

      def top_nodes(self, num, phi_ref, context_no, key_ref, path):
          contexts = []
          weighted_katz = self.katz_w_weight(path)
          katz_vals = [weighted_katz[label] for i, label in enumerate(context_no)] 
          df = pd.DataFrame()
          df['context'] = context_no
          df['key_ref'] = key_ref
          df['katz_vals'] = katz_vals
          print('num')
          print(num)
          for i in phi_ref:
              df_subset = df.loc[df['key_ref'] == i]
              if len(df_subset) > num:
                  df_subset.sort_values(by = 'katz_vals', ascending=False)
                  conts = df_subset['context'][0:num]
                  [contexts.append(i) for i in conts]
              else:
                  conts = df_subset['context']
                  [contexts.append(i) for i in conts]
          return contexts
        
      def graph_adjust(self, phase, phase_ref):
              if phase not in self.master.key_ref:
                  self.master.phi_ref.pop(phase_ref)                                
                  if self.master.prev_phase[phase_ref] == 'start':
                      phase_node = [i for i in self.master.chrono_dag.nodes() if "b_"+str(phase) in i]
                      self.master.chrono_dag.remove_node("a_" + str(phase))       
                      old_label = str(phase_node[0])
                      new_label = "a_"+ str(self.master.phi_ref[phase_ref + 1])
                      mapping = {old_label: new_label}
                      self.master.prev_phase.pop(phase_ref)
                      self.master.post_phase.pop(phase_ref)   
                      self.master.prev_phase[phase_ref] = 'start'
                  elif self.master.post_phase[phase_ref] == 'end':
                      phase_node = [i for i in self.master.chrono_dag.nodes() if "a_"+str(phase) in i]
                      self.master.chrono_dag.remove_node("b_" + str(phase))     
                      old_label = str(phase_node[0])
                      new_label = "b_"+ str(self.master.phi_ref[phase_ref -1])
                      mapping = {old_label: new_label}
                      self.master.prev_phase.pop(phase_ref)
                      self.master.post_phase.pop(phase_ref)   
                      self.master.post_phase[phase_ref] = 'end'
                  else:
                      phase_nodes = [i for i in self.master.chrono_dag.nodes() if phase in i]
                      self.master.chrono_dag = nx.contracted_nodes(self.master.chrono_dag, phase_nodes[0], phase_nodes[1]) 
                      new_label_1 = str(phase_nodes[0])
                      new_label = new_label_1.replace("a_"+str(phase), "a_"+ str(self.master.phi_ref[phase_ref + 1]))
                      mapping = {phase_nodes[0]: new_label}
                      self.master.prev_phase.pop(phase_ref)
                      self.master.post_phase.pop(phase_ref)   
                      self.master.prev_phase[phase_ref] = 'gap'
                      self.master.post_phase[phase_ref] = 'gap'
                  self.master.chrono_dag = nx.relabel_nodes(self.master.chrono_dag, mapping)
                  self.master.chrono_dag = phase_relabel(self.master.chrono_dag)
              self.master.chrono_dag.graph['graph']={'splines':'ortho'}    
              atribs = nx.get_node_attributes(self.master.chrono_dag, 'Group')
              nodes = self.master.chrono_dag.nodes()
              edge_add = []
              edge_remove = []
              for v,w in enumerate(self.master.CONTEXT_NO):
                    ####find paths in that phase
                    if self.master.CONT_TYPE[v] == 'residual':
                        phase = atribs[w]
                        root = [i for i in nodes if "b_" + str(phase) in i][0]
                        leaf = [i for i in nodes if "a_" + str(phase) in i][0]
                        all_paths = []
                        all_paths.extend(nx.all_simple_paths(self.master.chrono_dag, source = root, target = leaf))
                        for f in all_paths:
                            ind = np.where(np.array(f) == str(w))[0][0]
                            edge_add.append((f[ind - 1], f[ind+ 1]))
                        for k in self.master.chrono_dag.edges():
                            if k[0] == w:
                                edge_remove.append((k[0], k[1]))
                    elif self.master.CONT_TYPE[v] == 'intrusive':
                        for k in self.master.chrono_graph.edges():
                            if k[1] == w:
                                edge_remove.append((k[0], k[1]))
              for a in edge_add:
                    self.master.chrono_graph.add_edge(a[0], a[1], arrowhead = 'none')
              for b in edge_remove:
                    self.master.chrono_graph.remove_edge(b[0], b[1])


      def make_directories(self, i):         
              dirs2 = os.path.join(i, "stratigraphic_graph")
              dirs3 = os.path.join(i, "chronological_graph")
              dirs4 = os.path.join(i, "python_only")
              dirs5 = os.path.join(i, "mcmc_results")
              os.makedirs(dirs2)
              os.makedirs(dirs3)
              os.makedirs(dirs4)
              os.makedirs(dirs5)
              os.chdir(i)
              return dirs4
      def selectall(self):
          self.e.select_set(0, 'end')
    
      def save_state_1(self, master, j):
        
         vars_list_1 = dir(self.master)
         var_list = [var for var in vars_list_1 if (('__' and 'grid' and 'get' and 'tkinter' and 'children') not in var) and (var[0] != '_')]          
         data = {}
         check_list = ["tkinter", "method", "__main__", 'PIL']
         for i in var_list:
             v = getattr(master, i)
             if not any(x in str(type(v)) for x in check_list):
                data[i] = v
         data['all_vars'] = list(data.keys())
         data['load_check'] = globals.load_check
         data['mcmc_check'] = globals.mcmc_check
         data["file_input"] = globals.FILE_INPUT
         path = os.getcwd() + "/python_only/save.pickle"
         if globals.mcmc_check == 'mcmc_loaded': 
                results = data["all_results_dict"]
                df = pd.DataFrame()
                for i in results.keys():
                    df[i] = results[i][10000:]  
                results_path = os.getcwd() + "/mcmc_results/full_results_df"    
                df.to_csv(results_path)
                phasefile = data['phasefile']
                context_no = data['CONTEXT_NO']
                key_ref = [list(phasefile["Group"])[list(phasefile["context"]).index(i)] for i in context_no]
                df1 = pd.DataFrame(key_ref)   
                df1.to_csv('mcmc_results/key_ref.csv') 
                df2 = pd.DataFrame(context_no)
                df2.to_csv('mcmc_results/context_no.csv') 

         try:
             with open(path, "wb") as f:
                  pickle.dump(data, f)
         except Exception:
             tk.messagebox.showerror('Error', 'File not saved')        
             
      def load_cal_data(self, j):
         with open(self.path + "/" + str(j) + '/python_only/save.pickle', "rb") as f:
             data = pickle.load(f)
             vars_list = data['all_vars']
             for i in vars_list:
                 setattr(self, i, data[i])
             globals.FILE_INPUT = data['file_input']
             globals.load_check = data['load_check']
             globals.mcmc_check = data['mcmc_check']
