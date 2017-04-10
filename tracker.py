#Budget Software
# Copyright (c) 2016 Brandon Marder. All rights reserved.

#Import modules
import csv
import sys
from datetime import datetime, date

#today's date 
DAY_NOW = date.today()

def toDate(dateStr):
	return datetime.strptime(dateStr, '%m/%d/%Y')

#returns int of summed budget for a category. Used in sumBudgets function.
def getTotalBudget(categoryInfo):
	budget = 0
	startRow = categoryInfo[0]
	for row in categoryInfo[1:]:
		months = monthDist(startRow['Date'], row['Date'])
		budget += startRow['Amount'] * months
		startRow = row
	#budget contribution from last row until current month
	#***This is a problem if the first row is a transfer
	months = monthDist(startRow['Date'], DAY_NOW) + 1
	budget += months * startRow['Amount']
	
	return budget

def sumBudgets(categories):
	budgets = {}
	for key in categories:
		budgets[key] = getTotalBudget(categories[key])
	return budgets	

#Subtracts date2 - date1)
def monthDist(date1, date2):
	monthsDate1 = (date1.year * 12) + date1.month
	monthsDate2 = (date2.year * 12) + date2.month
	return (monthsDate2 - monthsDate1)


#Needs categories and expenses.
def sumExpenses(categories, expenses):
	categoriesList = [key for key in categories]
	expenseDictionary = {}
	for category in expenses:
		if category != 'Transfer' and category not in categoriesList:
			print (category + ' is an invalid category for an expense. Please check expense list')
			return
	for expenseCategory in expenses:
		amounts = [row['Amount'] for row in expenses[expenseCategory]]
		expenseDictionary[expenseCategory] = sum(amounts)
	#print expenseDictionary
	return expenseDictionary
			
#Calcualtes budget +/- . Needs summedExpenses and summedBudget 
def calculateDeltas(summedExpenses, summedBudget):
	deltas = {}
	for categoryName in summedBudget:
		if categoryName not in summedExpenses:
			deltas[categoryName] = summedBudget[categoryName]
		else:
			deltas[categoryName] = summedBudget[categoryName] - summedExpenses[categoryName]
	
	return deltas

#calculates total expenses by category for current and (month - 1). Needs expenses and a date
def calculateExpensesByMonth(expenses, month, monthOffset):
	expenseForMonth = {}
	for category in expenses:
		expenseForMonth[category] = 0
		for row in expenses[category]:
			if row['Transfer'] == True:
				continue
			if monthDist(row['Date'], month) == monthOffset:
				expenseForMonth[category] += row['Amount']
	return expenseForMonth
	
def calculateExpensesSinceMonth(expensens, month, monthOffset):
	expensesSinceMonth = {}
	for category in expenses:
		expensesSinceMonth[category] = 0
		for row in expenses[category]:
			if row['Transfer'] == True:
				continue
			if monthDist(row['Date'], month) <= monthOffset:
				expensesSinceMonth[category] += row['Amount']
	
#calculates whether budget balances
def determineIfOverBudget():
	annualIncome = input('Enter gross annual income: ')
	taxRate = input('Enter effective tax rate (e.g. 0.32): ')
	netIncome = annualIncome * (1 - taxRate)
	budgetDelta = sum(priorMonthExpenses.values()) - (netIncome / 12)
	budgetDelta = round(budgetDelta, 2)
	return budgetDelta
	
def askUserToDetermineOverBudget():
	userRequest = input('Would you like to check if your budget exceeds your income? (y/n)')
	if userRequest == 'y':
		return 'y'
	else:
		return 'n'
def main():
	#Create empty list for line items in budget
	categories = {}
	expenses = {}
	transfers = {}
	currentMonthExpenses = {}
	priorMonthExpenses = {}
	
	
	#Reads budget CSV file. These are the source of the categories used in the program.
	with open('budget.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if len(row['Category']) == 0:
				continue
			if row['Category'] not in categories:
				categories[row['Category']] = []
			row['Date'] = toDate(row['Date'])
			row['Amount'] = int(row['Amount'])
			categories[row['Category']].append(row)
	summedBudgets = sumBudgets(categories)	
	
	#Reads expenses CSV file. These are expenses for the categories in budget.csv
	with open('expenses.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if len(row['Category']) == 0:
				continue
			if row['Category'] == 'Transfer':
				if row['Category'] not in expenses:
					expenses[row['Category']] = []
				deductFrom = row['From']
				addTo = row['To']
				transferAmount = int(row['Amount'])
				#Adding to account
				summedBudgets[addTo] += transferAmount
				#Deducting from account
				summedBudgets[deductFrom] -= transferAmount
				continue
			if row['Category'] not in expenses:
				expenses[row['Category']] = []
			row['Amount'] = int(row['Amount'])
			row['Date'] = toDate(row['Date'])
			row['Transfer'] = False
			expenses[row['Category']].append(row)

	#Budgets summation row ~50
	summedExpenses = sumExpenses(categories, expenses)
	
	deltas = calculateDeltas(summedExpenses, summedBudgets)
	categoryNames = deltas.keys()
	categoryNames.sort()
	monthToDateExpenses = calculateExpensesByMonth(expenses, DAY_NOW, 0)
	priorMonthExpenses = calculateExpensesByMonth(expenses, DAY_NOW, 1)
	#calculateBudgetDelta = askUserToDetermineOverBudget()
	#if calculateBudgetDelta == 'y'
	#	determineIfOverBudget()
	print
	print ("Total expenses month to date:")
	for name in sorted(monthToDateExpenses):
		print name, monthToDateExpenses[name]
	print ("Total: %d" % sum(monthToDateExpenses.values()))
	print
	print ("Total expenses prior month:")
	for name in sorted(priorMonthExpenses):
		print name, priorMonthExpenses[name]
	print ("Total: %d" % sum(priorMonthExpenses.values()))
	print
	print ("Amount remaining in budget:")
	for name in categoryNames:
		print name, deltas[name]
	print ("Total: %d" % sum(deltas.values()))
	print 
	

		
if __name__ == '__main__':
	main()

