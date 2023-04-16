function statusbtn(status){
    if(status == "all"){
        $('.NonActive').removeClass("d-none");
        $('.Active').removeClass("d-none");
    }else if(status == "active"){
        $('.NonActive').addClass("d-none");
        $('.Active').removeClass("d-none");
    }else if(status == "inactive"){
        $('.NonActive').removeClass("d-none");
        $('.Active').addClass("d-none");
    }
}


function fetchCompany(){                
    document.getElementById('companiesData').innerHTML = ""
    document.getElementById('totalcompanyfetch').innerHTML = 0
    var companyname = $('#name-field').val();
    var countrycode = $('#country-field').val();
    var companytype = $('#company-type-field').val();
    if (companyname != "" && countrycode != ""){
        $('#searchbtn').text('Plz wait..');
        $('input[name="exampleRadios"]').prop('checked', false);
        $.ajax({
            type : "POST",
            url : "/fetch-company-list/",
            data : {"companyname":companyname, "countrycode":countrycode, "companytype":companytype},
            success : function(response) {     
                if(response.success == true){
                    document.getElementById('totalcompanyfetch').innerHTML = response.total
                    if (response.total == 0){
                        swal("Oops!", "No records found", "warning");
                    }else{
                        companies = response.companiesList 
                        for(var i = 0;i<response.total;i++){                                        
                            var content = "" 
                            regno = companies[i].RegistrationNumber                                         
                            if (regno == null){
                                console.log(regno)  
                                regno = ""
                            }             
                            vatno = companies[i].VatNumber   
                            if (vatno == null){
                                vatno = ""
                            }       
                            status = companies[i].Status 
                            content = "<tr class="+status+" onclick='clickReport(this)' id='"+companies[i].Id+"'><td>"+(i+1)+"</td><td>"+companies[i].Name+"</td><td>"+status+"</td><td>"+regno+"</td><td>"+vatno+"</td><td>"+companies[i].Address.SimpleValue+"</td><td>"+companies[i].DateOfLatestAccounts+"</td><td>"+companies[i].Id+"</td></tr>";
                            // setTimeout(() => { document.getElementById('companiesData').innerHTML += content; }, 200);
                            document.getElementById('companiesData').innerHTML += content;
                        }
                        $('#searchbtn').text('Search')
                    }                                
                }else{
                    swal("Oops!", "Something went wrong", "warning");
                }
                $('#searchbtn').text('Search')
            }                        
            });
    }else{
        swal("Oops!", "Company name and Country code are required.", "warning");
    }
    // $('#searchbtn').text('Search');
}

function clickReport(event){
    document.getElementById('modalCompaniesData2').innerHTML = "";     
    $('#default-example-modal-lg-center').modal('show');
    tr =  document.getElementById(event.id).innerHTML;                
    document.getElementById('modalCompaniesData1').innerHTML = tr;
    tr = document.getElementById('modalCompaniesData1');
    regno = tr.getElementsByTagName('td')[3].innerHTML;
    $.ajax({
        type : "POST",
        url : "/fetch-company-list-db/",
        data : {"regno":regno},
        success : function(response) {                        
            if(response.success == true){
                companies = response.company;
                content = "<tr id='"+companies.Id+"'><td>"+1+"</td><td>"+companies.name+"</td><td>"+companies.status+"</td><td>"+companies.regno+"</td><td>"+companies.address+"</td><td>"+companies.reportid+"</td><td>"+companies.fy+"</td><td>"+companies.lpd+"</td><td>"+companies.verifiedon+"</td></tr>";
                document.getElementById('modalCompaniesData2').innerHTML = content;
                $('#saveorupdate').text('Update');
            }else{
                $('#saveorupdate').text('Buy Report');
            }
        }                        
        });
}

function openOrderInvest(event){
    document.getElementById('orderCompaniesData1').innerHTML = "";
    $.ajax({
        type : "POST",
        url : "/fetch-order-list-db/",
        data : {},
        success : function(response) {                     
            if(response.success == true){
                orders = response.orders;
                for(var i = 0;i<orders.length;i++){                                        
                    var content = ""    
                    content = "<tr id="+orders[i].OrderId+" onclick='fetchordercompany(this)'><td>"+orders[i].OrderId+"</td><td>"+orders[i].Name+"</td><td>"+orders[i].OrderType+"</td><td>"+orders[i].regno+"</td><td>"+orders[i].Address+"</td><td>"+orders[i].ispdf+"</td><td>"+orders[i].deldate+"</td><td>"+orders[i].country+"</td><td class='d-none'>"+orders[i].countrycode+"</td></tr>";
                    document.getElementById('orderCompaniesData1').innerHTML += content;
                    $('#default-example-modal-lg-right').modal('show');
                }
            }else{
                swal("Oops!", "No orders found", "warning");
            }
        }                        
        });
}

function fetchordercompany(event){
    id = event.id;
    tr = document.getElementById(id);
    companyname = tr.getElementsByTagName('td')[1].innerHTML;
    countrycode = tr.getElementsByTagName('td')[8].innerHTML;
    $('#name-field').val(companyname);
    $('#country-field').val(countrycode);
    $('#default-example-modal-lg-right').modal('hide');
    fetchCompany()
}

function BuyReport(event){
    swal("", "Operation successfull.", "success");
}