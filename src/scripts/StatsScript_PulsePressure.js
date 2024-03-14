function getPulsePressureStats(stats) {
    let res = []
    let systolic_pressure = stats.find(st => st.code == 'systolic_pressure')
    let diastolic_pressure = stats.find(st => st.code == 'diastolic_pressure')

    if (systolic_pressure != null && diastolic_pressure != null) {
        let pp_data = []
        let map_data = []
        systolic_pressure.data.forEach((s, index) => {
            let d = diastolic_pressure.data[index]
            map_data.push((s - d) / 3 + d)
            pp_data.push(s - d)
        })

        res.push({
            name: 'Среднее давление (MAP)',
            code: 'map',
            avg: Math.ceil(map_data.reduce((a, b) => a + b, 0) / map_data.length),
            min: Math.ceil(map_data.reduce((a, b) => Math.min(a, b))),
            max: Math.ceil(map_data.reduce((a, b) => Math.max(a, b)))
        })

        res.push({
            name: 'Пульсовое давление',
            code: 'pulse_pressure',
            avg: Math.ceil(pp_data.reduce((a, b) => a + b, 0) / pp_data.length),
            min: Math.ceil(pp_data.reduce((a, b) => Math.min(a, b))),
            max: Math.ceil(pp_data.reduce((a, b) => Math.max(a, b)))
        })
    }

    return res
}

export default getPulsePressureStats