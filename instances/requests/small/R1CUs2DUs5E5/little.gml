graph [
  node [
    id 0
    label "0"
    type 2
    prc 4
  ]
  node [
    id 1
    label "1"
    type 2
    prc 2
  ]
  node [
    id 2
    label "2"
    type 1
    prc 3
    ant 1
    prb 2
    x 59
    y 60
  ]

  edge [
    source 1
    target 2
    bandwith 100
    delay 329
  ]
  edge [
    source 0
    target 2
    bandwith 100
    delay 483
  ]
]
