import os
import tkinter as tk
from PIL import ImageTk
from networkx.drawing.nx_pydot import write_dot
import networkx as nx
import numpy as np
import pandas as pd
from tkinter.filedialog import askopenfile
import pickle

class popupWindow8(object):
    # Not sure how this is differnet than Model.save in general. 
    # Triggered during cleanup. 
    def save_state_1(self, j):
        global mcmc_check, load_check, FILE_INPUT
        
        vars_list_1 = dir(self)
        var_list = [var for var in vars_list_1 if (('__' and 'grid' and 'get' and 'tkinter' and 'children') not in var) and (var[0] != '_')]          
        data = {}
        check_list = ["tkinter", "method", "__main__", 'PIL']
        for i in var_list:
            v = getattr(self, i)
            if not any(x in str(type(v)) for x in check_list):
               data[i] = v
        data['all_vars'] = list(data.keys())
        data['load_check'] = load_check
        data['mcmc_check'] = mcmc_check
        data["file_input"] = FILE_INPUT
        path = self.path + "/" +  str(j) + "/python_only/save.pickle"
        try:
            with open(path, "wb") as f:
                 pickle.dump(data, f)
            tk.messagebox.showinfo('Success', 'Your model has been saved')
        except Exception:
            tk.messagebox.showerror('Error', 'File not saved')             
    def load_cal_data(self, j):
        global mcmc_check, load_check, FILE_INPUT
        with open(self.path + "/" + str(j) + '/python_only/save.pickle', "rb") as f:
            data = pickle.load(f)
            vars_list = data['all_vars']
            for i in vars_list:
                setattr(self, i, data[i])
            FILE_INPUT = data['file_input']
            load_check = data['load_check']
            mcmc_check = data['mcmc_check']

# @todo - not implemented yet, no tkinter code so didn't fit the pattern of other popup classes
# When runnign this, cli output coutns from 0 to 100 mutliple times, with the occasional "File not saved" due to pickle erroring.
class popupWindow9(object):
      def __init__(self, master, path):
          global mcmc_check
          self.master = master
          self.path = path
          model_list_labels = [(str(path) + '/graph_theory_tests_' + str(i), i, 'graph_theory_tests_' + str(i)) for i in self.master.graph.nodes()]
  #        model_list = []
          ref_wd = os.getcwd()
          base_cont_type =  self.master.CONT_TYPE
          base_key_ref = self.master.key_ref
          base_context_no = self.master.CONTEXT_NO
          base_graph = self.master.graph
          base_chrono_graph = self.master.chrono_dag
          base_phi_ref = self.master.phi_ref
          base_prev_phase = self.master.prev_phase
          base_post_phase = self.master.post_phase
          base_context_no_unordered = self.master.context_no_unordered
          # RCD_EST = [int(list(self.master.datefile["date"])[list(self.master.datefile["context"]).index(i)]) for i in base_context_no]
          # RCD_ERR = [int(list(self.master.datefile["error"])[list(self.master.datefile["context"]).index(i)]) for i in base_context_no]
          # A = max(min(RCD_EST) - 4*max(RCD_EST), 0)
          # P = min(max(RCD_EST) + 4*max(RCD_EST), 50000)

          self.rc_llhds_dict = {}
          for i, j, k in model_list_labels:
              if k not in os.listdir(path):
                  os.chdir(ref_wd)
                  self.master.CONT_TYPE = base_cont_type.copy()
                  self.master.key_ref = base_key_ref.copy()
                  self.master.CONTEXT_NO = base_context_no.copy()
                  self.master.graph = base_graph.copy()
                  self.master.chrono_dag = base_chrono_graph.copy()
                  self.master.phi_ref = base_phi_ref.copy()
                  self.master.prev_phase = base_prev_phase.copy()
                  self.master.post_phase = base_post_phase.copy()    
                  self.master.context_no_unordered = base_context_no_unordered.copy()
                  #remove_node_section   
                  self.master.chrono_dag = node_del_fixed(self.master.chrono_dag, j)
                  self.master.graph = node_del_fixed(self.master.graph, j)
                  ref = np.where(np.array(base_context_no) == str(j))[0][0]
                  ref2 = np.where(np.array(base_context_no_unordered) == str(j))[0][0]
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
                  dirs4 = self.make_directories(i)
                  write_dot(self.master.chrono_dag, 'fi_new_chrono')
                  imgrender2(self.master.littlecanvas2.winfo_width(), self.master.littlecanvas2.winfo_height())  
                  imgrender(self.master.graph, self.master.littlecanvas.winfo_width(), self.master.littlecanvas.winfo_height())
                  self.master.ACCEPT = [[]]
                  while min([len(i) for i in self.master.ACCEPT]) < 20000:
                          self.master.CONTEXT_NO, self.master.ACCEPT, self.master.PHI_ACCEPT, self.master.PHI_REF, self.master.A, self.master.P, self.master.ALL_SAMPS_CONT, self.master.ALL_SAMPS_PHI, self.master.resultsdict, self.master.all_results_dict = self.master.MCMC_func()
                  mcmc_check = 'mcmc_loaded'
                  self.save_state_1(self.master, dirs4)

      def prob_overlap(self, ll1, ll2):
        ### hellenger distance
          dist_probs = np.array([(np.sqrt(ll2[1][i])-np.sqrt(j))**2 for i,j in enumerate(ll1[1])])
          h = 1 - 1/np.sqrt(2)*(np.sqrt(np.sum(dist_probs)))
          return h

        
      def node_importance(self, graph):
           G = graph.to_undirected() # setting up undirected graph          
           df_prob_overlap = pd.concat([pd.DataFrame([[str(i), str(j), self.prob_overlap(self.rc_llhds_dict[j], self.rc_llhds_dict[i])]], columns = ['node', 'neighbour', 'overlap_measure']) for i in G.nodes() for j in list(G.neighbors(i))])
          #katz
           df_prob_overlap.to_csv('overlap_df.csv')
           dd = nx.pagerank(G, alpha=0.85, personalization=None, max_iter=100, tol=1e-06, nstart=None, weight='weight', dangling=None)
           df = pd.DataFrame.from_dict(dd, orient = 'index')
           df.reset_index(inplace=True)
           df.columns = ['context', 'pagerank']
           df.to_csv("katz_centr.csv")
       
      def graph_adjust(self, phase, phase_ref):
              graph_check = nx.transitive_reduction(self.master.chrono_dag)
              if self.master.chrono_dag.edges() != graph_check.edges():
                 edges1 = list(self.master.chrono_dag.edges()).copy()
                 for k in edges1:
                     if k not in graph_check.edges():
                         self.master.chrono_dag.remove_edge(k[0], k[1])
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
                      self.master.chrono_dag.remove_edge(phase_nodes[0], phase_nodes[1])
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
                        for k in self.master.chrono_dag.edges():
                            if k[1] == w:
                                edge_remove.append((k[0], k[1]))
              for a in edge_add:
                    self.master.chrono_dag.add_edge(a[0], a[1], arrowhead = 'none')
              for b in edge_remove:
                    self.master.chrono_dag.remove_edge(b[0], b[1])


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
         global mcmc_check, load_check, FILE_INPUT
        
         vars_list_1 = dir(self.master)
         var_list = [var for var in vars_list_1 if (('__' and 'grid' and 'get' and 'tkinter' and 'children') not in var) and (var[0] != '_')]          
         data = {}
         check_list = ["tkinter", "method", "__main__", 'PIL']
         for i in var_list:
             v = getattr(master, i)
             if not any(x in str(type(v)) for x in check_list):
                data[i] = v
         data['all_vars'] = list(data.keys())
         data['load_check'] = load_check
         data['mcmc_check'] = mcmc_check
         data["file_input"] = FILE_INPUT
         path = j + "/save.pickle"
         if mcmc_check == 'mcmc_loaded': 
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
         global mcmc_check, load_check, FILE_INPUT
         with open(self.path + "/" + str(j) + '/python_only/save.pickle', "rb") as f:
             data = pickle.load(f)
             vars_list = data['all_vars']
             for i in vars_list:
                 setattr(self, i, data[i])
             FILE_INPUT = data['file_input']
             load_check = data['load_check']
             mcmc_check = data['mcmc_check']

# @todo - not implemented yet, no tkinter code so didn't fit the pattern of other popup classes
# FileNotFoundError: [Errno 2] No such file or directory: '/home/ptheywood/Documents/Pythonapp_tests/projects/demo/reference_model/python_only/save.pickle'
class popupWindow10(object):
      def __init__(self, master, path):
          global mcmc_check
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
              mcmc_check = 'mcmc_loaded'
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
         global mcmc_check, load_check, FILE_INPUT
        
         vars_list_1 = dir(self.master)
         var_list = [var for var in vars_list_1 if (('__' and 'grid' and 'get' and 'tkinter' and 'children') not in var) and (var[0] != '_')]          
         data = {}
         check_list = ["tkinter", "method", "__main__", 'PIL']
         for i in var_list:
             v = getattr(master, i)
             if not any(x in str(type(v)) for x in check_list):
                data[i] = v
         data['all_vars'] = list(data.keys())
         data['load_check'] = load_check
         data['mcmc_check'] = mcmc_check
         data["file_input"] = FILE_INPUT
         path = os.getcwd() + "/python_only/save.pickle"
         if mcmc_check == 'mcmc_loaded': 
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
         global mcmc_check, load_check, FILE_INPUT
         with open(self.path + "/" + str(j) + '/python_only/save.pickle', "rb") as f:
             data = pickle.load(f)
             vars_list = data['all_vars']
             for i in vars_list:
                 setattr(self, i, data[i])
             FILE_INPUT = data['file_input']
             load_check = data['load_check']
             mcmc_check = data['mcmc_check']

class load_Window(object):
    # @note - this was triggered after a model was created. Not yet (fully) reimplemetned @todo
    def create_file(self, folder_dir, load):  
        dirs = os.path.join(POLYCHRON_PROJECTS_DIR, folder_dir, self.model.get())
        dirs2 = os.path.join(dirs, "stratigraphic_graph")
        dirs3 = os.path.join(dirs, "chronological_graph")
        dirs4 = os.path.join(dirs, "python_only")
        dirs5 = os.path.join(dirs, "mcmc_results")
        if not os.path.exists(dirs):
       #     os.makedirs(dirs)
            os.makedirs(dirs)
            os.makedirs(dirs2)
            os.makedirs(dirs3)
            os.makedirs(dirs4)
            os.makedirs(dirs5)
            os.chdir(dirs)
            proj_dir = os.path.join(POLYCHRON_PROJECTS_DIR, folder_dir)
            if load:
                for F in (StartPage, PageOne):
                    page_name = F.__name__
                    frame = F(parent=self.master.container, controller=self.master)
                    self.master.frames[page_name] = frame
    
                    # put all of the pages in the same location;
                    # the one on the top of the stacking order
                    # will be the one that is visible.
                    frame.grid(row=0, column=0, sticky="nsew")        
                    self.master.show_frame("StartPage")   
            self.cleanup()
            tk.messagebox.showinfo('Tips:','model created successfully!')
            os.chdir(dirs)
        else:
            
            tk.messagebox.showerror('Tips','The folder name exists, please change it')
            self.cleanup()

class StartPage(tk.Frame):

    def save_state_1(self):
        global mcmc_check, load_check, FILE_INPUT
        #converting metadata treeview to dataframe
        row_list = []
        columns = ('context', 'Reason for deleting')
        for child in self.tree2.get_children():
            row_list.append((self.tree2.item(child)['text'],self.tree2.item(child)['values']))
        self.treeview_df = pd.DataFrame(row_list, columns=columns)
        vars_list_1 = dir(self)
  #      self.node_importance(self.graph)
        var_list = [var for var in vars_list_1 if (('__' and 'grid' and 'get' and 'tkinter' and 'children') not in var) and (var[0] != '_')]          
        data = {}
        # Type names to not pickle when saving state. polychron is excluded to avoid classes which inherit from tk, this may be a bit too strong.
        check_list = ["tkinter", "method", "__main__", 'PIL', "polychron"]
        

        for i in var_list:
            v = getattr(self, i)
            if not any(x in str(type(v)) for x in check_list):
               data[i] = v
        data['all_vars'] = list(data.keys())
        data['load_check'] = load_check
        data['mcmc_check'] = mcmc_check
        data["file_input"] = FILE_INPUT
        if mcmc_check == 'mcmc_loaded': 
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
        path = os.getcwd() + "/python_only/save.pickle"
        path2 = os.getcwd() + "/stratigraphic_graph/deleted_contexts_meta"
        self.treeview_df.to_csv(path2)
        try:
            with open(path, "wb") as f:
                 pickle.dump(data, f)
        except Exception as e:
                  print("error saving state:", str(e))

                
    def restore_state(self):
        global mcmc_check, load_check, FILE_INPUT
        with open('python_only/save.pickle', "rb") as f:
            data = pickle.load(f)
            vars_list = data['all_vars']
            for i in vars_list:
                setattr(self, i, data[i])
            FILE_INPUT = data['file_input']
            load_check = data['load_check']
            mcmc_check = data['mcmc_check']
        if self.graph is not None:
            self.littlecanvas.delete('all')
            self.rerender_stratdag()
            for i, j in enumerate(self.treeview_df['context']):
                 self.tree2.insert("", 'end', text=j, values=self.treeview_df['Reason for deleting'][i])

        if load_check == 'loaded':
            FILE_INPUT = None
            #manaually work this out as canvas hasn't rendered enough at this point to have a height and width in pixels
            height = 0.96*0.99*0.97*1000*0.96
            width = 0.99*0.37*2000*0.96  
            self.image2 = imgrender2(width, height)
            if self.image2 != 'No_image':
                self.littlecanvas2.delete('all')
                self.littlecanvas2.img = ImageTk.PhotoImage(self.image2)
                self.littlecanvas2_img = self.littlecanvas2.create_image(0, 0, anchor="nw",
                                                                         image=self.littlecanvas2.img)
    
                self.width2, self.height2 = self.image2.size
              #  self.imscale2 = 1.0  # scale for the canvaas image
                self.delta2 = 1.1  # zoom magnitude
                # Put image into container rectangle and use it to set proper coordinates to the image
                self.container2 = self.littlecanvas2.create_rectangle(0, 0, self.width2, self.height2, width=0)
                self.imscale2  = min(921/self.image2.size[0], 702/self.image2.size[1])
                self.littlecanvas.scale('all', 0, 0, self.delta2, self.delta2)  # rescale all canvas objects       
                self.show_image2()
                
                self.littlecanvas2.bind("<Configure>", self.resize2)


    def rerender_stratdag(self):
        global phase_true
        """rerenders stratdag after reloading previous project"""
        height = 0.96 * 0.99 * 0.97 * 1000
        width = 0.99 * 0.37 * 2000 * 0.96
        if phase_true == 1:
            self.image = imgrender_phase(self.graph)
        else:
            self.image = imgrender(self.graph, width, height)

        #       self.image = self.image_ws.resize((int(self.image_ws.size[0]*scale_factor), int(self.image_ws.size[1]*scale_factor)), Image.ANTIALIAS)
        self.littlecanvas.img = ImageTk.PhotoImage(self.image)
        self.littlecanvas_img = self.littlecanvas.create_image(0, 0, anchor="nw", image=self.littlecanvas.img)

        self.width, self.height = self.image.size
        #   self.imscale = 1.0  # scale for the canvaas image
        self.delta = 1.1  # zoom magnitude
        # Put image into container rectangle and use it to set proper coordinates to the image
        self.container = self.littlecanvas.create_rectangle(0, 0, self.width, self.height, width=0)
        self.imscale = min(width / self.image.size[0], height / self.image.size[1])

        self.delnodes = []
        self.delnodes_meta = []
        self.littlecanvas.bind("<Button-3>", self.preClick)
        self.littlecanvas.update()
        self.littlecanvas.scale("all", 0, 0, self.delta, self.delta)  # rescale all canvas objects
        self.show_image()