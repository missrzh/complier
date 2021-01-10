.386
.model flat, stdcall
option casemap:none
include C://masm32/include/masm32rt.inc 
main PROTO
.data
.code

start:
    invoke main
    fn MessageBox,0,str$(eax), "Lab5" ,MB_OK
    invoke ExitProcess, 0
    
hello PROC
push ebp
mov ebp, esp
mov eax, DWORD ptr[ebp+8]
push eax
mov eax, 1
mov ebx, eax
pop eax
add eax, ebx
mov DWORD ptr[ebp+8], eax
mov eax, DWORD ptr[ebp+8]
mov esp, ebp
pop ebp
ret
mov esp, ebp
pop ebp

ret
hello ENDP
goodbuy PROC
push ebp
mov ebp, esp
mov eax, DWORD ptr[ebp+8]
push eax
mov eax, 1
mov ebx, eax
pop eax
sub eax, ebx
mov DWORD ptr[ebp+8], eax
mov eax, DWORD ptr[ebp+8]
mov esp, ebp
pop ebp
ret
mov esp, ebp
pop ebp

ret
goodbuy ENDP
main PROC
push ebp
mov ebp, esp
mov eax, 6
push eax
mov eax, DWORD ptr[ebp+-4]

push eax
call hello
add esp, 4
mov DWORD ptr[ebp+-4], eax
mov eax, DWORD ptr[ebp+-4]

push eax
call hello
add esp, 4
mov DWORD ptr[ebp+-4], eax
mov eax, DWORD ptr[ebp+-4]

push eax
call goodbuy
add esp, 4
mov DWORD ptr[ebp+-4], eax
mov eax, DWORD ptr[ebp+-4]
mov esp, ebp
pop ebp
ret
mov esp, ebp
pop ebp

ret
main ENDP

END start