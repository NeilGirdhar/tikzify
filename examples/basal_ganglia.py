from __future__ import annotations

from edge_colors import EDGE_COLORS  # type: ignore[import-not-found]

from tikzify import (Alignment, EdgeSpecification, IntersectionAnchor, NodeAnchor, NodeContainer,
                     NodeGraph, NodePosition, NodeText, RelativeAnchor, TerminalSpacing, TextSize,
                     create_links, tex_file, tex_pic)

dimmed_opacity = 0.18
node_size = (13.0, 11.0)
w = 0.8
terminal_spacing = TerminalSpacing(horizontal=[0.0, 0.8, w / 2, w / 3, w / 4, w / 5],
                                   vertical=[0.0, 0.5, 0.4, 0.3])


links = [
    # --------------------------------------------------------------------------------------
    # Subthalamic links.
    *[EdgeSpecification(source, target, to, ['all'], ['complete', 'stn'],
                        via=(True, ['right_of_gpep2'] if target.startswith('below') else []))
      for source, target, to in [('above_stn0', 'right_of_gpep0', 'recognition'),
                                 ('above_stn4', 'left_of_gpi0', 'recognition'),
                                 ('above_stn1', 'below_gpen2', 'attention'),
                                 ('above_stn3', 'below_sncv0', 'attention')]],
    EdgeSpecification('above_stn2', 'below_sncd0', 'pooling', ['all'], ['complete', 'stn']),

    # --------------------------------------------------------------------------------------
    # Nigro-cortical links.
    EdgeSpecification('above_sncv0', 'below_ctxpt0', 'control', ['all'],
                      ['complete', 'strp']),  # negate

    # Nigro-striatal links.
    # negate
    EdgeSpecification('above_sncv1', 'strm_sncv1', 'control', ['all'], ['complete', 'strp']),
    # negate
    EdgeSpecification('above_sncv2', 'strp_sncv2', 'explanation', ['all'], ['complete', 'strp']),
    EdgeSpecification('above_sncd0', 'strm_sncd0', 'recognition', ['all'], ['complete', 'strm']),

    # Nigro-nigral link.
    # negate
    EdgeSpecification('left_of_sncv0', 'right_of_sncd0', 'recognition', ['all'], ['complete']),

    # --------------------------------------------------------------------------------------
    # Striato-nigral links.
    EdgeSpecification('strp_sncv3', 'above_sncv3', 'explanation', ['all'], ['complete', 'strp']),
    EdgeSpecification('strm_sncd1', 'above_sncd1', 'deduction', ['all'], ['complete', 'strm']),

    # Striato-striatal links.
    # negate
    EdgeSpecification('above_strp', 'below_strm', 'deduction', ['all'], ['complete']),

    # Striato-pallidal links.
    EdgeSpecification('striatum_gpen', 'above_gpen0', 'explanation', ['all'], ['complete', 'strm']),
    EdgeSpecification('below_strmi0', 'left_of_gpep0', 'control', ['all'], ['complete', 'strm'],
                      via=(True, [])),
    EdgeSpecification('below_strmd0', 'right_of_gpi1', 'control', ['all'], ['complete', 'strm'],
                      via=(True, [])),
    EdgeSpecification('below_strpi0', 'above_gpep0', 'explanation', ['all'], ['complete', 'strp']),
    EdgeSpecification('below_strpd0', 'above_gpi0', 'explanation', ['all'], ['complete', 'strp']),

    # --------------------------------------------------------------------------------------
    # Pallido-nigral link.
    EdgeSpecification('left_of_gpi2', 'below_sncv2', 'gln', ['all'], ['complete', 'strm'],
                      via=(False, [])),

    # Pallido-pallidal links.
    EdgeSpecification('right_of_gpep2', 'below_gpen0', 'gln', ['all'], ['complete', 'strm'],
                      via=(False, [])),
    EdgeSpecification('right_of_gpep1', 'left_of_gpi1', 'explanation', ['all'],
                      ['complete', 'strm']),

    # Pallido-thalamic link.
    # negate
    EdgeSpecification('right_of_gpi0', 'left_of_tha0', 'control', ['all'], ['complete', 'strm']),
    # negate
    EdgeSpecification('below_gpep0', 'left_of_trn0', 'control', ['all'], ['complete', 'strm'],
                      via=(True, [])),
    EdgeSpecification('right_of_trn0', 'below_tha0', 'gln', ['all'], ['complete', 'strm'],
                      via=(False, [])),

    # Pallido-subthalamic link.
    EdgeSpecification('below_gpen1', 'left_of_stn0', 'attention', ['all'], ['complete', 'stn'],
                      via=(True, [])),

    # --------------------------------------------------------------------------------------
    # Cortico-striatal links.
    EdgeSpecification('below_ctxpt3', 'strm_ctxpt', 'pooling', ['all'], ['complete', 'strm']),
    # Dashed lines indicates a diffuse link.
    EdgeSpecification('below_ctxit0', 'strp_ctxit', 'pooling', ['all'], ['complete', 'strm'],
                      dash='densely dashdotted'),

    # Hyper-direct pathway.
    EdgeSpecification('right_of_ctxpt1', 'right_of_stn0', 'pooling', ['all'], ['complete', 'stn'],
                      via=(False, ['thalamo_cortical1'])),

    # --------------------------------------------------------------------------------------
    # Thalamo-cortical link.
    # negate
    EdgeSpecification('right_of_tha0', 'right_of_ctxpt0', 'explanation', ['all'],
                      ['complete', 'strm'],
                      via=(False, ['thalamo_cortical0'])),

    # Exogenous signals.
    EdgeSpecification('reward_in', 'below_sncv1', 'pooling', ['all'], ['complete']),
    EdgeSpecification('policy_in', 'below_tha1', 'pooling', ['all'], ['complete']),
]


with tex_file('basal_ganglia.tex',
              ['latex/includes',
               'latex/commands',
               'tikz/base',
               'tikz/color_macros',
               'tikz/extra_tips',
               'tikz/cma_tips',
               'tikz/flow_style']) as f:
    for diagram in ['complete',
                    # 'strp', 'strm', 'stn',
                    ]:
        node_graph = NodeGraph(edge_colors=EDGE_COLORS)

        def create_rectangular_node(node_name: str,
                                    position: NodePosition,
                                    node_text: NodeText,
                                    ng: NodeGraph = node_graph) -> None:
            ng.create_node(node_name, position, text=node_text, size=node_size, shape='rectangle')

        g = node_graph.digraph
        with tex_pic(f, 'basal_ganglia-' + diagram, 'Flow diagram, /CMA tips'):
            # Create nodes.
            y = 2.4
            for name, direction in [('strmi', 'left'), ('strmd', 'right')]:
                d = {direction: 5.5}
                create_rectangular_node(name,
                                        NodePosition(NodeAnchor('str_center'), above=y, **d),
                                        NodeText([rf'$\{name}$']))
            for name, direction in [('strpi', 'left'), ('strpd', 'right')]:
                d = {direction: 4.0}
                create_rectangular_node(name,
                                        NodePosition(NodeAnchor('str_center'), **d),
                                        NodeText([rf'$\{name}$']))
            create_rectangular_node('sncd',
                                    NodePosition(NodeAnchor('str_center'), below=2.5),
                                    NodeText([r'$\sncd$']))
            create_rectangular_node('gpen',
                                    NodePosition(NodeAnchor('sncd'), left=2.5),
                                    NodeText([r'$\gpen$']))
            create_rectangular_node('sncv',
                                    NodePosition(NodeAnchor('sncd'), right=2.5),
                                    NodeText([r'$\sncv$']))
            create_rectangular_node('gpi',
                                    NodePosition(IntersectionAnchor('strpd', 'gpi_center')),
                                    NodeText([r'$\gpi$']))
            create_rectangular_node('gpep',
                                    NodePosition(IntersectionAnchor('strpi', 'gpi_center')),
                                    NodeText([r'$\gpep$']))
            create_rectangular_node('stn',
                                    NodePosition(NodeAnchor('sncd'), below=3.6),
                                    NodeText([r'$\stn$']))
            create_rectangular_node('tha',
                                    NodePosition(NodeAnchor('right_of_gpi0'), right=1.2),
                                    NodeText([r'$\tha$']))
            create_rectangular_node('trn',
                                    NodePosition(NodeAnchor('gpi'), below=2.6),
                                    NodeText([r'$\trn$']))
            for name, vertical in (('ctxit', 'gpen'), ('ctxpt', 'sncv')):
                create_rectangular_node(name,
                                        NodePosition(IntersectionAnchor(vertical, 'ctx_center')),
                                        NodeText([rf'$\{name}$']))

            # Create inputs and outputs.
            node_graph.create_io('reward_in',
                                 NodeText(['reward', 'input'],
                                          align=Alignment.center, color='dcoloro',
                                          size=TextSize.footnote, standard_height=True),
                                 'bottom_edge',
                                 'below_sncv1')
            node_graph.create_io('policy_in',
                                 NodeText(['policy', 'input'],
                                          align=Alignment.center, color='dcoloro',
                                          size=TextSize.footnote, standard_height=True),
                                 'bottom_edge',
                                 'below_tha1')

            # Create containers.
            for name, text, group in [('striatum', 'Striatum', [f'str{b}{a}'
                                                                for a in 'di'
                                                                for b in 'mp']),
                                      ('strp', 'Striatal patch', [f'strp{a}' for a in 'di']),
                                      ('strm', 'Striatal matrix', [f'strm{a}' for a in 'di']),
                                      # ('snc', 'SNc', ['sncd', 'sncv']),
                                      ]:
                node_graph.create_node(name,
                                       None,
                                       container=NodeContainer(
                                           group,
                                           corner_text=NodeText([text], size=TextSize.footnote)),
                                       inner_sep=12 if name == 'striatum' else 5,
                                       shape='rectangle, draw',
                                       color='dcolorr',
                                       dash='dashed')

            # Create terminals.
            node_graph.create_node_terminals('ctxit', terminal_spacing, 0, 0, 0, 1)
            node_graph.create_node_terminals('ctxpt', terminal_spacing, 0, 2, 0, 4)
            node_graph.create_node_terminals('gpi', terminal_spacing, 3, 2, 1, 0)
            node_graph.create_node_terminals('gpep', terminal_spacing, 1, 3, 1, 1)
            node_graph.create_node_terminals('gpen', terminal_spacing, 0, 0, 1, 3)
            node_graph.create_node_terminals('sncv', terminal_spacing, 1, 0, 4, 3)
            node_graph.create_node_terminals('sncd', terminal_spacing, 0, 1, 2, 1)
            node_graph.create_node_terminals('strpi', terminal_spacing, 0, 0, 0, 1)
            node_graph.create_node_terminals('strpd', terminal_spacing, 0, 0, 0, 1)
            node_graph.create_node_terminals('strmi', terminal_spacing, 0, 0, 0, 1)
            node_graph.create_node_terminals('strmd', terminal_spacing, 0, 0, 0, 1)
            node_graph.create_node_terminals('stn', terminal_spacing, 1, 1, 5, 0)
            node_graph.create_node_terminals('tha', terminal_spacing, 1, 1, 0, 2)
            node_graph.create_node_terminals('trn', terminal_spacing, 1, 1, 0, 0)

            # Create coordinates.
            for str_group, anchor, horizontal, name in [
                ('strp', 'north', 'below_ctxit0', 'strp_ctxit'),
                ('strm', 'north', 'below_ctxpt3', 'strm_ctxpt'),
                ('striatum', 'south', 'above_gpen0', 'striatum_gpen'),
                ('strm', 'south', 'above_sncd0', 'strm_sncd0'),
                ('strm', 'south', 'above_sncd1', 'strm_sncd1'),
                ('strm', 'south', 'above_sncv1', 'strm_sncv1'),
                ('strp', 'south', 'above_sncv2', 'strp_sncv2'),
                ('strp', 'south', 'above_sncv3', 'strp_sncv3'),
                ('strm', 'south', 'below_ctxpt3', 'below_strm'),
                ('strp', 'north', 'below_ctxpt3', 'above_strp'),
            ]:
                node_graph.create_coordinate(
                    name,
                    NodePosition(IntersectionAnchor(horizontal, RelativeAnchor(str_group, anchor))))
            node_graph.create_coordinate('str_center', (0, 0))
            node_graph.create_coordinate('ctx_center',
                                         NodePosition(NodeAnchor('str_center'), above=6.0))
            node_graph.create_coordinate('gpi_center', NodePosition(NodeAnchor('sncd'), below=1.8))
            node_graph.create_coordinate(
                'thalamo_cortical0',
                NodePosition(RelativeAnchor('striatum', 'east'), right=0.4))
            node_graph.create_coordinate(
                'thalamo_cortical1',
                NodePosition(NodeAnchor('thalamo_cortical0'), right=0.4))
            node_graph.create_coordinate('str_above',
                                         NodePosition(RelativeAnchor('striatum', 'north'),
                                                      above=0.3))
            node_graph.create_edges('striatum', 'thalamo_cortical1', 'ctxpt', 'trn', margin=0.5)

            create_links(node_graph, links, dimmed_opacity, [diagram])
            node_graph.generate(f)
