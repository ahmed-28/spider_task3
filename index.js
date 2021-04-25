  
console.log("happy");


var year_labels = [];
var year_revenue = [];
var month_label = [];
var month_revenue = [];
var week_label = [];
var week_revenue = [];

function drawChart(data,labels){
    console.log(data);
    var chart = new Chartist.Line('.ct-chart', {
    labels: labels,
    series: [
        data
    ]
    }, {
    low: 0,
    showArea: true,
    showPoint: false,
    fullWidth: true
    });
    chart.on('draw', function(data) {
    if(data.type === 'line' || data.type === 'area') {
        data.element.animate({
        d: {
            begin: 2000 * data.index,
            dur: 2000,
            from: data.path.clone().scale(1, 0).translate(0, data.chartRect.height()).stringify(),
            to: data.path.clone().stringify(),
            easing: Chartist.Svg.Easing.easeOutQuint
        }
        });
    }
    });
}

function parsefiles(e,file_type){
    let file = e.target.files[0];



    let reader = new FileReader();

    reader.onload = () => {
            let result = reader.result;
            let values = result.split("\n");

            let size = values.length;
            
            //yearly
            let rev = 0,days=365;
            for(let i=size-1;i>=0;i--){
                if(days>0){
                    rev += Number(values[i]);
                    days = days - 1;
                }
                else{
                    console.log(rev);
                    year_revenue.push(rev);
                    rev=0;
                    days=365;
                    year_labels.push("year");
                    
                }
            }
            if(rev>0){
                year_revenue.push(rev);
                year_labels.push('year');
            }
            drawChart(year_revenue,year_labels);
            //monthly
            days = 30;rev=0;
            for(let i=size-1;i>=0;i--){
                if(days>0){

                    rev += Number(values[i]);
                    days = days - 1;
                }
                else{
                    console.log(rev);
                    month_revenue.push(rev);
                    rev=0;
                    days=30;
                    month_label.push("month");
                    
                }
            }
            if(rev>0){
                month_revenue.push(rev);
                month_label.push('month');
            }

            //weekly
            days = 7;rev=0;
            for(let i=size-1;i>=0;i--){
                if(days>0){

                    rev += Number(values[i]);
                    days = days - 1;
                }
                else{
                    week_revenue.push(rev);
                    rev=0;
                    days=7;
                    week_label.push("week");
                    
                }
            }
            if(rev>0){
                week_revenue.push(rev);
                week_label.push('week');
            }


    }

    reader.readAsText(file);
    
}

document.getElementById("totalinput").addEventListener('change',(e)=>{

    parsefiles(e);
});

function change_active(type){
    let div = document.getElementById(type);
    document.getElementsByClassName("active column")[0].className = "column";
    div.className = "active column";
    if(type=="year")
        drawChart(year_revenue,year_labels);
    else if(type =="month")
        drawChart(month_revenue,month_label);
    else
        drawChart(week_revenue,week_label);
}


